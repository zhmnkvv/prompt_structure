"""Count Claude tokens for each prompt and each part of the structured prompts.

This fills the values marked `Not measured` in results/token-analysis.md
(section "Token breakdown of the good prompts"). It calls the Anthropic Token
Counting endpoint (POST /v1/messages/count_tokens), which returns the exact
input_tokens the model would see. It does not generate text.

Requirements:
    pip install anthropic
    an API key in ANTHROPIC_API_KEY (or a profile from `ant auth login`)

Usage:
    python scripts/count_prompt_tokens.py

Notes:
    * Each count includes a small fixed overhead for the message wrapper, so the
      script also counts an empty-ish message ("-") and reports counts with that
      baseline subtracted.
    * Counts are model-specific; this uses the model that ran the experiments.
"""
import json
import re
from pathlib import Path

from anthropic import Anthropic

MODEL = "claude-opus-5-5"
ROOT = Path(__file__).resolve().parents[1]
SECTION_RE = re.compile(r"^(TASK|CONTEXT|FORMAT|EXAMPLE):\s*$", re.M)
# Lines of the EXAMPLE block that are rules rather than the example template.
REQUIREMENT_RE = re.compile(r"^(Не придумывай|Сначала найди).*$", re.M)

client = Anthropic()


def count(text: str) -> int:
    return client.messages.count_tokens(
        model=MODEL, messages=[{"role": "user", "content": text}]
    ).input_tokens


def split_parts(prompt: str) -> dict:
    marks = list(SECTION_RE.finditer(prompt))
    parts = {}
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(prompt)
        parts[m.group(1)] = prompt[m.start():end].strip()
    example = parts.get("EXAMPLE", "")
    reqs = "\n".join(REQUIREMENT_RE.findall(example))
    parts["EXAMPLE"] = REQUIREMENT_RE.sub("", example).strip()
    parts["REQUIREMENTS"] = reqs
    return parts


def main():
    base = count("-")
    result = {"model": MODEL, "wrapper_baseline_tokens": base, "prompts": {}}
    for f in sorted((ROOT / "prompts").glob("*.txt")):
        text = f.read_text(encoding="utf8").strip()
        entry = {"total_tokens": count(text) - base}
        if f.stem.endswith("good"):
            entry["parts"] = {k: count(v) - base for k, v in split_parts(text).items()}
        result["prompts"][f.stem] = entry
        print(f.stem, entry)
    out = ROOT / "results" / "data" / "prompt_token_counts.json"
    out.write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf8")
    print("saved", out)


if __name__ == "__main__":
    main()
