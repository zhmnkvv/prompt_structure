"""Collect real token usage, cost and timing for the prompt-structure experiments.

Reads the Claude Code subagent transcripts (JSONL) of the four runs and the
prompt texts, and writes results/data/usage_metrics.json.

Every number comes from the `usage` objects the Anthropic API returned for each
request (input_tokens, cache_creation_input_tokens with its 5m/1h split,
cache_read_input_tokens, output_tokens, output_tokens_details.thinking_tokens)
and from the transcript timestamps. Nothing is estimated.

Usage:
    python scripts/analyze_usage.py <subagents_dir>
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Official Anthropic pricing for claude-opus-5-5, USD per 1M tokens.
# Source: https://platform.claude.com/docs/en/about-claude/pricing (checked 2026-11-12)
PRICE = {"input": 4.00, "cache_write_5m": 5.00, "cache_write_1h": 8.00,
         "cache_read": 0.20, "output": 20.00}

RUNS = {
    "task1": {"bad": "aadbf9525e2230446", "good": "a5d765e1535de3a27"},
    "task2": {"bad": "ac04f72bd8dcbf381", "good": "abdc1b9e797d9c01c"},
}
# Wall-clock run time of each subagent, as reported by the Claude Code harness
# in its task-completion notification (duration_ms).
HARNESS_DURATION_MS = {
    "aadbf9525e2230446": 126908, "a5d765e1535de3a27": 137239,
    "ac04f72bd8dcbf381": 170971, "abdc1b9e797d9c01c": 340547,
}

SECTION_RE = re.compile(r"^(TASK|CONTEXT|FORMAT|EXAMPLE):\s*$", re.M)


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def cost(u):
    return (u["input"] * PRICE["input"] + u["cache_write_5m"] * PRICE["cache_write_5m"]
            + u["cache_write_1h"] * PRICE["cache_write_1h"]
            + u["cache_read"] * PRICE["cache_read"] + u["output"] * PRICE["output"]) / 1e6


def text_stats(t):
    return {"chars": len(t), "words": len(t.split())}


def components(prompt):
    """Split a structured prompt into its TASK / CONTEXT / FORMAT / EXAMPLE parts."""
    parts, marks = {}, list(SECTION_RE.finditer(prompt))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(prompt)
        parts[m.group(1)] = text_stats(prompt[m.end():end].strip())
    return parts


def read_run(path):
    calls, events = {}, []
    for line in open(path, encoding="utf8"):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        events.append(e)
        m = e.get("message") or {}
        if m.get("role") == "assistant" and "usage" in m:
            calls[e.get("requestId") or m.get("id")] = (e, m)
    rows = []
    for e, m in calls.values():
        u = m["usage"]
        cc = u.get("cache_creation") or {}
        rows.append({
            "model": m.get("model"), "speed": u.get("speed"), "service_tier": u.get("service_tier"),
            "effort": e.get("effort"), "timestamp": e["timestamp"],
            "input": u.get("input_tokens", 0),
            "cache_write_5m": cc.get("ephemeral_5m_input_tokens", 0),
            "cache_write_1h": cc.get("ephemeral_1h_input_tokens", 0),
            "cache_read": u.get("cache_read_input_tokens", 0),
            "output": u.get("output_tokens", 0),
            "thinking": (u.get("output_tokens_details") or {}).get("thinking_tokens", 0),
        })
    # Generation time of the final answer: from the last event before the final
    # assistant request (the tool result it answers) to the final assistant entry.
    last = rows[-1]
    last_t = ts(last["timestamp"])
    prev = [ts(e["timestamp"]) for e in events if e.get("timestamp")
            and ts(e["timestamp"]) < last_t and (e.get("message") or {}).get("role") == "user"]
    final_gen_s = (last_t - max(prev)).total_seconds() if prev else None
    return rows, final_gen_s


def summarize(rows):
    keys = ["input", "cache_write_5m", "cache_write_1h", "cache_read", "output", "thinking"]
    s = {k: sum(r[k] for r in rows) for k in keys}
    s["prompt_side"] = s["input"] + s["cache_write_5m"] + s["cache_write_1h"] + s["cache_read"]
    s["total"] = s["prompt_side"] + s["output"]
    s["cost_usd"] = cost(s)
    s["cost_if_no_cache_usd"] = (s["prompt_side"] * PRICE["input"] + s["output"] * PRICE["output"]) / 1e6
    return s


def main(subdir):
    subdir = Path(subdir)
    out = {"pricing_usd_per_mtok": PRICE,
           "pricing_source": "https://platform.claude.com/docs/en/about-claude/pricing",
           "pricing_checked": "2026-11-12", "experiments": {}}
    for task, pair in RUNS.items():
        out["experiments"][task] = {}
        for ver, aid in pair.items():
            rows, final_gen = read_run(subdir / f"agent-{aid}.jsonl")
            prompt = (ROOT / "prompts" / f"{task}-{ver}.txt").read_text(encoding="utf8").strip()
            answer = (ROOT / "results" / "data" / "answers" / f"{task}-{ver}.md").read_text(encoding="utf8").strip()
            first, last = rows[0], rows[-1]
            final = {k: last[k] for k in ["input", "cache_write_5m", "cache_write_1h", "cache_read", "output", "thinking"]}
            final["prompt_side"] = final["input"] + final["cache_write_5m"] + final["cache_write_1h"] + final["cache_read"]
            final["cost_usd"] = cost(final)
            out["experiments"][task][ver] = {
                "model": sorted({r["model"] for r in rows}),
                "speed": sorted({r["speed"] for r in rows}),
                "service_tier": sorted({r["service_tier"] for r in rows}),
                "effort": sorted({str(r["effort"]) for r in rows}),
                "api_calls": len(rows),
                "first_request_prompt_tokens": first["input"] + first["cache_write_5m"]
                + first["cache_write_1h"] + first["cache_read"],
                "run": summarize(rows),
                "final_answer_request": final,
                "final_answer_generation_s": final_gen,
                "run_wall_clock_s": HARNESS_DURATION_MS[aid] / 1000,
                "prompt": text_stats(prompt),
                "prompt_components": components(prompt) if ver == "good" else None,
                "response": text_stats(answer),
                "calls": rows,
            }
        e = out["experiments"][task]
        e["prompt_token_delta_good_minus_bad"] = (e["good"]["first_request_prompt_tokens"]
                                                  - e["bad"]["first_request_prompt_tokens"])
    dst = ROOT / "results" / "data" / "usage_metrics.json"
    dst.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf8")
    for task in RUNS:
        for ver in ("bad", "good"):
            x = out["experiments"][task][ver]
            print(task, ver, x["api_calls"], x["first_request_prompt_tokens"], x["run"]["total"],
                  x["run"]["output"], round(x["run"]["cost_usd"], 4), x["final_answer_request"]["output"],
                  round(x["final_answer_request"]["cost_usd"], 4), x["final_answer_generation_s"],
                  x["prompt"], x["response"])
        print(task, "delta", out["experiments"][task]["prompt_token_delta_good_minus_bad"])


if __name__ == "__main__":
    main(sys.argv[1])
