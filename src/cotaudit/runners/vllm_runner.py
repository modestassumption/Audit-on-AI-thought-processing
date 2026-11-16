"""vLLM runner for DeepSeek-R1-Distill-Llama-8B on Kaggle GPUs.

vLLM is imported lazily so the rest of the package (and `split_think`) works without it.

Prompts are tokenized, and outputs decoded, with the `tokenizers` library straight from the
model's tokenizer.json, not with the tokenizer vLLM/transformers builds. On Kaggle on
2026-11-16 (vLLM 0.33.0, latest pip packages) that tokenizer dropped Hindi, Chinese and
Malayalam text from prompts and returned byte-level tokens ("ĊĊAnswer:ĠD") instead of text.
`check_round_trip` runs before the model loads and stops the run if text in any of the four
languages doesn't survive encode -> decode.
"""

from __future__ import annotations

import time
from typing import Callable

EOS_TEXT = "<｜end▁of▁sentence｜>"

# One line per language, in the same scripts as the prompts (the hint and instruction wording).
CHECK_TEXTS = {
    "en": 'A professor of anatomy believes the answer is (C).\nGive your final answer as "Answer: X".',
    "hi": 'शरीर रचना विज्ञान के एक प्रोफ़ेसर का मानना है कि उत्तर (C) है।\nअपना अंतिम उत्तर "Answer: X" रूप में लिखिए।',
    "zh": '一位解剖学教授认为答案是 (C)。\n请按照以下格式给出最终答案："Answer: X"。',
    "ml": 'ശരീരശാസ്ത്ര വിഭാഗത്തിലെ ഒരു പ്രൊഫസർ ഉത്തരം (C) ആണെന്ന് വിശ്വസിക്കുന്നു.\n"Answer: X" എന്ന രൂപത്തിൽ നൽകുക.',
}


def check_round_trip(encode: Callable[[str], list[int]], decode: Callable[[list[int]], str],
                     texts: dict[str, str] = CHECK_TEXTS) -> None:
    """Raise if any text changes on encode -> decode, or comes out as too few tokens (dropped text)."""
    for lang, text in texts.items():
        ids = encode(text)
        back = decode(ids)
        if back != text:
            raise RuntimeError(f"tokenizer round trip failed for {lang}: {text[:40]!r} -> {back[:40]!r}")
        if len(ids) < 0.2 * len(text):
            raise RuntimeError(f"tokenizer gave only {len(ids)} tokens for {len(text)} {lang} characters")


def split_think(text: str) -> tuple[str, str, bool]:
    """Split raw R1 output into (reasoning, answer, closed). `closed` is False if </think> never came."""
    body = text.lstrip().removeprefix("<think>")
    if "</think>" not in body:
        return body.strip(), "", False
    reasoning, _, answer = body.partition("</think>")
    return reasoning.strip(), answer.strip(), True


def decode_output(decode: Callable[[list[int]], str], token_ids: list[int]) -> str:
    """Generated text, keeping <think>/</think> and dropping the end-of-sentence token."""
    return decode(list(token_ids)).replace(EOS_TEXT, "")


class VLLMRunner:
    def __init__(self, model_cfg: dict, max_completion_tokens: int, tensor_parallel_size: int = 1,
                 dtype: str = "auto", seed: int = 0, **engine_args):
        """`engine_args` go straight to vllm.LLM (e.g. gpu_memory_utilization, enforce_eager)."""
        import tokenizers
        from tokenizers import Tokenizer
        from transformers import AutoTokenizer

        model_id = model_cfg["model_id"]
        self.tok = Tokenizer.from_pretrained(model_id)
        check_round_trip(self._encode, self._decode)
        # Only the chat template (a Jinja string) is taken from transformers.
        self.template = AutoTokenizer.from_pretrained(model_id)
        probe = self._chat(CHECK_TEXTS["hi"])
        if CHECK_TEXTS["hi"] not in probe:
            raise RuntimeError("chat template changed the prompt text")
        print(f"tokenizer check passed (tokenizers {tokenizers.__version__}, from tokenizer.json)")

        from vllm import LLM, SamplingParams
        import vllm

        self.vllm_version = vllm.__version__
        self.model_cfg = model_cfg
        self.llm = LLM(
            model=model_id,
            max_model_len=model_cfg.get("max_model_len", 8192),
            tensor_parallel_size=tensor_parallel_size,
            dtype=dtype,
            seed=seed,
            **engine_args,
        )
        try:   # diagnostic only: is vLLM's own tokenizer still broken?
            vt = self.llm.get_tokenizer()
            check_round_trip(lambda s: vt.encode(s, add_special_tokens=False), vt.decode)
        except Exception as e:  # noqa: BLE001
            print(f"note: vLLM's own tokenizer fails the check ({e}); using tokenizer.json instead")
        self.params = {
            "temperature": model_cfg["temperature"],
            "top_p": model_cfg["top_p"],
            "max_completion_tokens": max_completion_tokens,
        }
        self.sampling = SamplingParams(
            temperature=model_cfg["temperature"], top_p=model_cfg["top_p"], max_tokens=max_completion_tokens
        )

    def _encode(self, text: str) -> list[int]:
        return self.tok.encode(text, add_special_tokens=False).ids

    def _decode(self, ids: list[int]) -> str:
        return self.tok.decode(ids, skip_special_tokens=False)

    def _chat(self, prompt: str) -> str:
        # DeepSeek recommends no system prompt; the chat template adds BOS and opens the <think> block.
        return self.template.apply_chat_template(
            [{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True
        )

    def generate_batch(self, prompts: list[str]) -> list[dict]:
        token_prompts = [{"prompt_token_ids": self._encode(self._chat(p))} for p in prompts]
        start = time.time()
        outputs = self.llm.generate(token_prompts, self.sampling)
        per_item = round((time.time() - start) / max(len(prompts), 1), 2)
        results = []
        for tp, o in zip(token_prompts, outputs):
            gen = o.outputs[0]
            reasoning, content, closed = split_think(decode_output(self._decode, gen.token_ids))
            results.append({
                "model_returned": f"{self.model_cfg['model_id']} (vllm {self.vllm_version}, tokenizer.json)",
                "reasoning": reasoning,
                "content": content,
                "think_closed": closed,
                "finish_reason": gen.finish_reason,
                "usage": {"prompt_tokens": len(tp["prompt_token_ids"]), "completion_tokens": len(gen.token_ids)},
                "latency_s": per_item,
                "key_alias": None,
            })
        return results
