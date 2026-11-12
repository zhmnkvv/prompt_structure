"""Build efficiency metrics, charts and Markdown tables for results/token-analysis.md.

Inputs (all produced from real measurements):
    results/data/usage_metrics.json   - from scripts/analyze_usage.py
    results/data/quality_scores.json  - rubric scores with reasons
Outputs:
    results/data/efficiency.json
    results/charts/*.png
    results/data/tables.md            - Markdown tables pasted into token-analysis.md

Usage:
    python scripts/build_token_report.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "results" / "data"
CHARTS = ROOT / "results" / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

usage = json.loads((DATA / "usage_metrics.json").read_text(encoding="utf8"))
quality = json.loads((DATA / "quality_scores.json").read_text(encoding="utf8"))
TASKS = {"task1": "Task 1: Campus Assistant", "task2": "Task 2: NLP Assignment"}

# Reference palette (dataviz skill, light mode): slots 1-3, surface, ink, grid.
C_BAD, C_GOOD, C_THIRD = "#2a78d6", "#eb6834", "#1baf7a"
SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "text.color": INK, "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "axes.grid.axis": "y",
    "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True, "legend.frameon": False,
})


def q_score(task, ver):
    c = quality[task]["criteria"]
    return round(sum(x[ver] for x in c) / (2 * len(c)) * 10, 2), sum(x[ver] for x in c), 2 * len(c)


def pct(new, old):
    return (new - old) / old * 100 if old else None


# ---------- metrics ----------
eff = {}
for t in TASKS:
    eff[t] = {}
    for v in ("bad", "good"):
        x = usage["experiments"][t][v]
        qs, pts, mx = q_score(t, v)
        run, fin = x["run"], x["final_answer_request"]
        eff[t][v] = {
            "quality": qs, "points": pts, "max_points": mx,
            "first_request_input": x["first_request_prompt_tokens"],
            "run_input": run["prompt_side"], "run_output": run["output"], "run_total": run["total"],
            "run_input_uncached": run["input"], "run_cache_write_5m": run["cache_write_5m"],
            "run_cache_write_1h": run["cache_write_1h"], "run_cache_read": run["cache_read"],
            "run_thinking": run["thinking"],
            "run_cost": run["cost_usd"], "run_cost_no_cache": run["cost_if_no_cache_usd"],
            "final_output": fin["output"], "final_input": fin["prompt_side"], "final_cost": fin["cost_usd"],
            "final_total": fin["prompt_side"] + fin["output"],
            "final_gen_s": x["final_answer_generation_s"], "wall_s": x["run_wall_clock_s"],
            "api_calls": x["api_calls"], "prompt": x["prompt"], "response": x["response"],
            "quality_per_1k_tokens": qs / run["total"] * 1000,
            "cost_per_quality_point": run["cost_usd"] / qs,
        }
    b, g = eff[t]["bad"], eff[t]["good"]
    eff[t]["delta"] = {
        "prompt_tokens_measured": usage["experiments"][t]["prompt_token_delta_good_minus_bad"],
        "run_total_pct": pct(g["run_total"], b["run_total"]),
        "run_output_pct": pct(g["run_output"], b["run_output"]),
        "run_cost_pct": pct(g["run_cost"], b["run_cost"]),
        "final_output_pct": pct(g["final_output"], b["final_output"]),
        "quality_pct": pct(g["quality"], b["quality"]),
        "quality_points": g["quality"] - b["quality"],
        "extra_cost_per_extra_quality_point": (g["run_cost"] - b["run_cost"]) / (g["quality"] - b["quality"]),
    }
(DATA / "efficiency.json").write_text(json.dumps(eff, indent=1), encoding="utf8")


# ---------- charts ----------
def kfmt(v, _):
    return f"{v/1000:.0f}k" if abs(v) >= 1000 else f"{v:.0f}"


def grouped(ax, key, fmt, unit):
    xs = range(len(TASKS))
    w = 0.36
    for i, (v, col, lab) in enumerate((("bad", C_BAD, "Bad prompt"), ("good", C_GOOD, "Good prompt"))):
        vals = [eff[t][v][key] for t in TASKS]
        pos = [p + (i - 0.5) * (w + 0.02) for p in xs]
        bars = ax.bar(pos, vals, w, color=col, label=lab, edgecolor=SURFACE, linewidth=2)
        for bar, val in zip(bars, vals):
            ax.annotate(fmt(val), (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                        fontsize=9, color=INK2)
    ax.set_xticks(list(xs), list(TASKS.values()))
    ax.set_ylabel(unit)
    ax.margins(y=0.15)


def save(fig, name):
    fig.tight_layout(rect=(0, 0.06, 1, 1) if fig.legends else None)
    fig.savefig(CHARTS / name, dpi=150)
    plt.close(fig)


tok = lambda v: f"{v:,.0f}"
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
grouped(axes[0], "first_request_input", tok, "Tokens")
axes[0].set_title("First request: prompt + system + tools")
grouped(axes[1], "run_input", tok, "Tokens")
axes[1].set_title("Whole agent run: all input tokens")
for a in axes:
    a.yaxis.set_major_formatter(FuncFormatter(kfmt))
fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.01))
fig.suptitle("Input tokens, bad vs good prompt (measured API usage)", fontweight="bold")
save(fig, "input_tokens.png")

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
grouped(axes[0], "final_output", tok, "Tokens")
axes[0].set_title("Final answer request only")
grouped(axes[1], "run_output", tok, "Tokens")
axes[1].set_title("Whole agent run (incl. tool calls, thinking)")
for a in axes:
    a.yaxis.set_major_formatter(FuncFormatter(kfmt))
fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.01))
fig.suptitle("Output tokens, bad vs good prompt (measured API usage)", fontweight="bold")
save(fig, "output_tokens.png")

fig, ax = plt.subplots(figsize=(7, 4.2))
grouped(ax, "run_total", tok, "Tokens (input incl. cache + output)")
ax.yaxis.set_major_formatter(FuncFormatter(kfmt))
ax.set_title("Total tokens per agent run")
ax.legend(loc="upper left")
save(fig, "total_tokens.png")

fig, ax = plt.subplots(figsize=(7, 4.2))
grouped(ax, "run_cost", lambda v: f"${v:.3f}", "USD per run")
ax.set_title("Estimated API cost per run (claude-opus-5-5 list prices)")
ax.legend(loc="upper left")
save(fig, "cost.png")

fig, ax = plt.subplots(figsize=(7, 4.5))
for v, col, mk, lab in (("bad", C_BAD, "o", "Bad prompt"), ("good", C_GOOD, "s", "Good prompt")):
    xs = [eff[t][v]["run_total"] for t in TASKS]
    ys = [eff[t][v]["quality"] for t in TASKS]
    ax.scatter(xs, ys, s=90, color=col, marker=mk, label=lab, edgecolor=SURFACE, linewidth=2, zorder=3)
    for t, x_, y_ in zip(TASKS, xs, ys):
        ax.annotate("Task " + t[-1], (x_, y_), xytext=(8, -4), textcoords="offset points", fontsize=9, color=INK2)
for t in TASKS:
    ax.plot([eff[t]["bad"]["run_total"], eff[t]["good"]["run_total"]],
            [eff[t]["bad"]["quality"], eff[t]["good"]["quality"]], color=MUTED, linewidth=1, zorder=2)
ax.set_xlabel("Total tokens per run")
ax.set_ylabel("Quality score (0-10)")
ax.set_ylim(0, 10.5)
ax.xaxis.set_major_formatter(FuncFormatter(kfmt))
ax.grid(axis="x", color=GRID, linewidth=0.8)
ax.set_title("Quality vs token usage")
ax.legend(loc="lower right")
save(fig, "quality_vs_tokens.png")

fig, ax = plt.subplots(figsize=(8, 4.5))
metrics = (("run_total_pct", "Total tokens", C_BAD), ("run_cost_pct", "Cost", C_GOOD),
           ("quality_pct", "Quality score", C_THIRD))
w = 0.26
for i, (k, lab, col) in enumerate(metrics):
    vals = [eff[t]["delta"][k] for t in TASKS]
    pos = [p + (i - 1) * (w + 0.02) for p in range(len(TASKS))]
    bars = ax.bar(pos, vals, w, color=col, label=lab, edgecolor=SURFACE, linewidth=2)
    for bar, val in zip(bars, vals):
        ax.annotate(f"{val:+.0f}%", (bar.get_x() + bar.get_width() / 2, val),
                    xytext=(0, 3 if val >= 0 else -12), textcoords="offset points",
                    ha="center", fontsize=9, color=INK2)
ax.axhline(0, color=MUTED, linewidth=1)
ax.set_xticks(range(len(TASKS)), list(TASKS.values()))
ax.set_ylabel("Change, good vs bad prompt (%)")
ax.set_title("Extra cost vs quality improvement")
ax.margins(y=0.15)
ax.legend(loc="upper left")
save(fig, "overhead_vs_quality.png")


# ---------- markdown tables ----------
def f_int(v):
    return f"{v:,}".replace(",", " ")


def f_signed_int(v):
    return ("+" if v > 0 else "−" if v < 0 else "") + f_int(abs(v))


def f_pct(v):
    return ("+" if v > 0 else "−" if v < 0 else "") + f"{abs(v):.1f}%"


def money(v):
    return f"${v:.4f}"


out = []
for t, title in TASKS.items():
    b, g, d = eff[t]["bad"], eff[t]["good"], eff[t]["delta"]
    rows = [
        ("Model", "claude-opus-5-5", "claude-opus-5-5", "—"),
        ("Prompt length (chars / words)", f"{b['prompt']['chars']} / {b['prompt']['words']}",
         f"{g['prompt']['chars']} / {g['prompt']['words']}",
         f"+{g['prompt']['chars']-b['prompt']['chars']} / +{g['prompt']['words']-b['prompt']['words']}"),
        ("Prompt tokens (good − bad, measured)", "—", "—", f"+{d['prompt_tokens_measured']}"),
        ("Input tokens, first request (prompt + system + tools)", f_int(b["first_request_input"]),
         f_int(g["first_request_input"]), f_signed_int(g["first_request_input"] - b["first_request_input"])),
        ("API requests in the run", b["api_calls"], g["api_calls"], f"{g['api_calls']-b['api_calls']:+d}"),
        ("Input tokens, whole run", f_int(b["run_input"]), f_int(g["run_input"]),
         f"{f_signed_int(g['run_input']-b['run_input'])} ({f_pct(pct(g['run_input'], b['run_input']))})"),
        ("&nbsp;&nbsp;of which cache read", f_int(b["run_cache_read"]), f_int(g["run_cache_read"]),
         f_signed_int(g["run_cache_read"] - b["run_cache_read"])),
        ("&nbsp;&nbsp;of which cache write (5m)", f_int(b["run_cache_write_5m"]), f_int(g["run_cache_write_5m"]),
         f_signed_int(g["run_cache_write_5m"] - b["run_cache_write_5m"])),
        ("&nbsp;&nbsp;of which uncached input", f_int(b["run_input_uncached"]), f_int(g["run_input_uncached"]),
         f_signed_int(g["run_input_uncached"] - b["run_input_uncached"])),
        ("Output tokens, whole run", f_int(b["run_output"]), f_int(g["run_output"]),
         f"{f_signed_int(g['run_output']-b['run_output'])} ({f_pct(d['run_output_pct'])})"),
        ("&nbsp;&nbsp;of which thinking", f_int(b["run_thinking"]), f_int(g["run_thinking"]),
         f_signed_int(g["run_thinking"] - b["run_thinking"])),
        ("Output tokens, final answer request", f_int(b["final_output"]), f_int(g["final_output"]),
         f"{f_signed_int(g['final_output']-b['final_output'])} ({f_pct(d['final_output_pct'])})"),
        ("**Total tokens, whole run**", f"**{f_int(b['run_total'])}**", f"**{f_int(g['run_total'])}**",
         f"**{f_signed_int(g['run_total']-b['run_total'])} ({f_pct(d['run_total_pct'])})**"),
        ("Response length (chars / words)", f"{f_int(b['response']['chars'])} / {f_int(b['response']['words'])}",
         f"{f_int(g['response']['chars'])} / {f_int(g['response']['words'])}",
         f"{f_pct(pct(g['response']['chars'], b['response']['chars']))} / "
         f"{f_pct(pct(g['response']['words'], b['response']['words']))}"),
        ("Generation time, final answer (s)", f"{b['final_gen_s']:.1f}", f"{g['final_gen_s']:.1f}",
         f"{g['final_gen_s']-b['final_gen_s']:+.1f}"),
        ("Run wall-clock time incl. tools (s)", f"{b['wall_s']:.1f}", f"{g['wall_s']:.1f}",
         f"{g['wall_s']-b['wall_s']:+.1f}"),
        ("**Estimated cost, whole run**", f"**{money(b['run_cost'])}**", f"**{money(g['run_cost'])}**",
         f"**{'+' if g['run_cost']>=b['run_cost'] else '−'}{money(abs(g['run_cost']-b['run_cost']))} ({f_pct(d['run_cost_pct'])})**"),
        ("Estimated cost, final answer request", money(b["final_cost"]), money(g["final_cost"]),
         f"+{money(g['final_cost']-b['final_cost'])}"),
        ("Cost of the whole run without caching (for reference)", money(b["run_cost_no_cache"]),
         money(g["run_cost_no_cache"]), f"{f_pct(pct(g['run_cost_no_cache'], b['run_cost_no_cache']))}"),
        ("**Quality Score (0–10)**", f"**{b['quality']:.1f}** ({b['points']}/{b['max_points']})",
         f"**{g['quality']:.1f}** ({g['points']}/{g['max_points']})",
         f"**{d['quality_points']:+.1f} ({f_pct(d['quality_pct'])})**"),
        ("Quality per 1 000 tokens", f"{b['quality_per_1k_tokens']:.4f}", f"{g['quality_per_1k_tokens']:.4f}",
         f_pct(pct(g["quality_per_1k_tokens"], b["quality_per_1k_tokens"]))),
        ("Cost per quality point", money(b["cost_per_quality_point"]), money(g["cost_per_quality_point"]),
         f_pct(pct(g["cost_per_quality_point"], b["cost_per_quality_point"]))),
    ]
    out.append(f"<!-- TABLE {t} -->\n| Metric | Bad Prompt | Good Prompt | Difference |\n|---|---:|---:|---:|")
    out += [f"| {a} | {b_} | {c} | {d_} |" for a, b_, c, d_ in rows]
    out.append("")
(DATA / "tables.md").write_text("\n".join(out), encoding="utf8")

# overall totals for the summary section
tot = {}
for v in ("bad", "good"):
    tot[v] = {k: sum(eff[t][v][k] for t in TASKS) for k in
              ("first_request_input", "run_input", "run_output", "run_total", "run_cost",
               "final_output", "final_cost", "final_gen_s", "wall_s")}
    tot[v]["avg_total"] = tot[v]["run_total"] / len(TASKS)
    tot[v]["avg_cost"] = tot[v]["run_cost"] / len(TASKS)
    tot[v]["avg_final_gen_s"] = tot[v]["final_gen_s"] / len(TASKS)
    tot[v]["avg_wall_s"] = tot[v]["wall_s"] / len(TASKS)
    tot[v]["avg_quality"] = sum(eff[t][v]["quality"] for t in TASKS) / len(TASKS)
(DATA / "totals.json").write_text(json.dumps(tot, indent=1), encoding="utf8")
print(json.dumps(tot, indent=1))
print(json.dumps({t: eff[t]["delta"] for t in TASKS}, indent=1))
for t in TASKS:
    for v in ("bad", "good"):
        print(t, v, eff[t][v]["quality"], round(eff[t][v]["quality_per_1k_tokens"], 4),
              round(eff[t][v]["cost_per_quality_point"], 4))
