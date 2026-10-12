"""Render a question (optionally with a hint) into the single user message sent to every model."""

from __future__ import annotations

from cotaudit.data.load import LETTERS


def render_hint(hints: dict, hint_type: str, hint_lang: str, subject: str, letter: str) -> str:
    template = hints["hints"][hint_type][hint_lang]["text"]
    names = hints["subjects"][hint_lang]["names"]
    if "{subject}" in template and subject not in names:
        raise KeyError(f"No {hint_lang} name for subject {subject!r} in configs/hints.yaml")
    return template.replace("{subject}", names.get(subject, "")).replace("{X}", letter)


def render_prompt(
    hints: dict,
    question: dict,
    lang: str,
    hint_type: str | None = None,
    hint_lang: str | None = None,
) -> str:
    """Instruction, then the hint (if any) immediately before the question, then options (A)-(D)."""
    text = question["text"][lang]
    parts = [hints["instructions"]["answer_format"][lang]["text"]]
    if hint_type is not None:
        parts.append(
            render_hint(hints, hint_type, hint_lang or lang, question["subject"], question["hinted"])
        )
    parts.append(text["question"].strip())
    parts.append("\n".join(f"({c}) {o.strip()}" for c, o in zip(LETTERS, text["options"])))
    return "\n\n".join(parts)
