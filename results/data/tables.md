<!-- TABLE task1 -->
| Metric | Bad Prompt | Good Prompt | Difference |
|---|---:|---:|---:|
| Model | claude-opus-5-5 | claude-opus-5-5 | — |
| Prompt length (chars / words) | 215 / 30 | 1171 / 170 | +956 / +140 |
| Prompt tokens (good − bad, measured) | — | — | +410 |
| Input tokens, first request (prompt + system + tools) | 48 188 | 48 598 | +410 |
| API requests in the run | 8 | 6 | -2 |
| Input tokens, whole run | 498 000 | 371 772 | −126 228 (−25.3%) |
| &nbsp;&nbsp;of which cache read | 428 142 | 298 196 | −129 946 |
| &nbsp;&nbsp;of which cache write (5m) | 69 842 | 73 564 | +3 722 |
| &nbsp;&nbsp;of which uncached input | 16 | 12 | −4 |
| Output tokens, whole run | 6 606 | 10 679 | +4 073 (+61.7%) |
| &nbsp;&nbsp;of which thinking | 879 | 658 | −221 |
| Output tokens, final answer request | 4 853 | 9 510 | +4 657 (+96.0%) |
| **Total tokens, whole run** | **504 606** | **382 451** | **−122 155 (−24.2%)** |
| Response length (chars / words) | 9 496 / 1 482 | 22 511 / 3 669 | +137.1% / +147.6% |
| Generation time, final answer (s) | 52.1 | 86.0 | +33.9 |
| Run wall-clock time incl. tools (s) | 126.9 | 137.2 | +10.3 |
| **Estimated cost, whole run** | **$0.5670** | **$0.6411** | **+$0.0741 (+13.1%)** |
| Estimated cost, final answer request | $0.1211 | $0.2149 | +$0.0938 |
| Cost of the whole run without caching (for reference) | $2.1241 | $1.7007 | −19.9% |
| **Quality Score (0–10)** | **3.0** (6/20) | **9.5** (19/20) | **+6.5 (+216.7%)** |
| Quality per 1 000 tokens | 0.0059 | 0.0248 | +317.8% |
| Cost per quality point | $0.1890 | $0.0675 | −64.3% |

<!-- TABLE task2 -->
| Metric | Bad Prompt | Good Prompt | Difference |
|---|---:|---:|---:|
| Model | claude-opus-5-5 | claude-opus-5-5 | — |
| Prompt length (chars / words) | 132 / 19 | 1232 / 181 | +1100 / +162 |
| Prompt tokens (good − bad, measured) | — | — | +463 |
| Input tokens, first request (prompt + system + tools) | 48 174 | 48 637 | +463 |
| API requests in the run | 7 | 13 | +6 |
| Input tokens, whole run | 549 393 | 854 920 | +305 527 (+55.6%) |
| &nbsp;&nbsp;of which cache read | 448 027 | 766 288 | +318 261 |
| &nbsp;&nbsp;of which cache write (5m) | 101 352 | 88 604 | −12 748 |
| &nbsp;&nbsp;of which uncached input | 14 | 28 | +14 |
| Output tokens, whole run | 9 003 | 20 432 | +11 429 (+126.9%) |
| &nbsp;&nbsp;of which thinking | 1 643 | 2 072 | +429 |
| Output tokens, final answer request | 5 805 | 7 810 | +2 005 (+34.5%) |
| **Total tokens, whole run** | **558 396** | **875 352** | **+316 956 (+56.8%)** |
| Response length (chars / words) | 10 080 / 1 615 | 17 380 / 2 634 | +72.4% / +63.1% |
| Generation time, final answer (s) | 58.7 | 50.2 | -8.5 |
| Run wall-clock time incl. tools (s) | 171.0 | 340.5 | +169.6 |
| **Estimated cost, whole run** | **$0.7765** | **$1.0050** | **+$0.2285 (+29.4%)** |
| Estimated cost, final answer request | $0.1488 | $0.2166 | +$0.0678 |
| Cost of the whole run without caching (for reference) | $2.3776 | $3.8283 | +61.0% |
| **Quality Score (0–10)** | **5.5** (12/22) | **9.6** (21/22) | **+4.1 (+75.2%)** |
| Quality per 1 000 tokens | 0.0098 | 0.0109 | +11.8% |
| Cost per quality point | $0.1425 | $0.1052 | −26.1% |
