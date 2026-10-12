"""vLLM runner for DeepSeek-R1-Distill-Llama-8B on Kaggle GPUs.

vLLM is imported lazily so the rest of the package (and `split_think`) works without it.
"""

from __future__ import annotations

import time


def split_think(text: str) -> tuple[str, str, bool]:
    """Split raw R1 output into (reasoning, answer, closed). `closed` is False if </think> never came."""
    body = text.lstrip().removeprefix("<think>")
    if "</think>" not in body:
        return body.strip(), "", False
    reasoning, _, answer = body.partition("</think>")
    return reasoning.strip(), answer.strip(), True


class VLLMRunner:
    def __init__(self, model_cfg: dict, max_completion_tokens: int, tensor_parallel_size: int = 1,
                 dtype: str = "auto", seed: int = 0):
        from vllm import LLM, SamplingParams
        import vllm

        self.vllm_version = vllm.__version__
        self.model_cfg = model_cfg
        self.llm = LLM(
            model=model_cfg["model_id"],
            max_model_len=model_cfg.get("max_model_len", 8192),
            tensor_parallel_size=tensor_parallel_size,
            dtype=dtype,
            seed=seed,
        )
        self.tokenizer = self.llm.get_tokenizer()
        self.params = {
            "temperature": model_cfg["temperature"],
            "top_p": model_cfg["top_p"],
            "max_completion_tokens": max_completion_tokens,
        }
        self.sampling = SamplingParams(
            temperature=model_cfg["temperature"], top_p=model_cfg["top_p"], max_tokens=max_completion_tokens
        )

    def generate_batch(self, prompts: list[str]) -> list[dict]:
        # DeepSeek recommends no system prompt; the chat template opens the <think> block.
        texts = [
            self.tokenizer.apply_chat_template(
                [{"role": "user", "content": p}], tokenize=False, add_generation_prompt=True
            )
            for p in prompts
        ]
        start = time.time()
        outputs = self.llm.generate(texts, self.sampling)
        per_item = round((time.time() - start) / max(len(prompts), 1), 2)
        results = []
        for o in outputs:
            gen = o.outputs[0]
            reasoning, content, closed = split_think(gen.text)
            results.append({
                "model_returned": f"{self.model_cfg['model_id']} (vllm {self.vllm_version})",
                "reasoning": reasoning,
                "content": content,
                "think_closed": closed,
                "finish_reason": gen.finish_reason,
                "usage": {"prompt_tokens": len(o.prompt_token_ids), "completion_tokens": len(gen.token_ids)},
                "latency_s": per_item,
                "key_alias": None,
            })
        return results
