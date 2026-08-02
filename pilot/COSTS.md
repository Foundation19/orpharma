# Measured Claude costs

Every unit price used in the grant application's budget appears below with the token counts
and the derivation behind it. Two
kinds of operation are priced separately — a grounding pass and a judgement — and neither rate
is applied to the other's work.

Token counts are the `usage` fields returned by the API, deduplicated by `message.id`, summed
from agent transcripts. Dollar figures are those token counts **valued at Claude Opus 5 list
rates** — input USD 5.00/M, cache write USD 6.25/M, output USD 25.00/M, cache read USD 0.50/M —
because that is the denomination a credit award uses. They are not amounts billed; this work ran
on a flat-rate plan.

---

## 1. Fan-out rate for this project

All background agent work run on this project, across 1,112 agent transcripts and 9,702
billable messages:

| | Tokens |
|---|---:|
| Input | 3,060,208 |
| Cache write | 134,392,837 |
| Output | 4,172,317 |
| Cache read | 966,888,980 |
| **Total** | **1,108,514,342** |

At list rates that is USD 1,443, or **USD 1.30 per million total tokens.**

Cache read is 87.2% of all tokens, averaging 99,659 cache-read tokens per billable message —
far more than any single fixed prompt. What is being re-read is the accumulated context of a
long-running agent, not one cached rubric. **A workload with less context reuse would not get
this rate.**

**This is a subset, not the project total.** It covers background agent transcripts only. Metered
usage over six months comes to roughly **13.9 billion tokens** — 44.2M new input and output
against 13.67B cache reads — which converts to USD 9,194 at Opus 5 list rates.

---

## 2. Pilots

Run 2026-08-01 specifically to price the proposed grounding step. Real items drawn from
`orpharma_master_v2.2.jsonl`; no synthetic inputs.

Tier and strength notation: **T1** structured databases only, **T2** abstracts, **T3** primary
full text. **L2** requires a citable identifier per field; **L3** requires the supporting sentence
quoted verbatim, and a field with no such sentence is recorded `ungrounded` rather than filled
from model knowledge.

**Each price below is one grounding pass over one unit.** The budget's "three independent
sources" means three passes, each required to cite a source the others did not, so the ×3
multiplier is not double-counting a price that already covered three.

| Step | n | Items | Input | Cache write | Output | Cache read | Total | Cost | **Per unit** |
|---|--:|---|--:|--:|--:|--:|--:|--:|--:|
| Gene, T3/L3 | 3 | DPAGT1, TRMU, B4GALT1 | 2,135 | 148,788 | 3,333 | 3,966,496 | 4,120,752 | $3.01 | **$1.002** |
| Drug, T1+T2/L3 | 3 | L-aspartic acid, levacetylleucine, niacinamide | 115 | 100,294 | 5,496 | 1,765,424 | 1,871,329 | $1.65 | **$0.549** |
| Path, T1/L2 | 5 | rows 305, 2282, 400, 1574, 2476 | 136 | 101,395 | 12,371 | 6,025,732 | 6,139,634 | $3.96 | **$0.791** |

**The pilot is small: n = 3, 3 and 5.** The submitted budget bills 3,093 gene passes (1,031 genes x 3 independent
sources), 11,283 drug passes and 22,682 full-text item passes, so these prices are extrapolated
**1,031x, 3,761x and 4,536x** respectively.
Re-measurement after the first 100 units of each type is part of the plan, and the revised
figures will be published here.

**The largest risk in every price below is the cache-read share.** The three pilots ran
96.3%, 94.3% and 98.1% cache read, in single hot sessions of three to five units. At 22,682
full-text passes spread over months across heterogeneous documents that share is unlikely to
hold, and the prices scale with it: at 50% cache read the gene pass costs roughly 4x what the
pilot measured. Nothing here establishes that the share survives production, and no evidence
either way exists yet. The first-100 re-measurement is where it is settled.

### Judgement operations, measured separately

A grounding pass and a judgement are different operations and are priced separately. Ten real
items from `orpharma_master_v2.2.jsonl` were judged on Opus by the judging procedure — read
the procedure once, then judge ten in sequence, writing the full gate / Step 0 / Step A / Step B
chain for each, as a production labelling run would.

| | Tokens | Per judgement |
|---|---:|---:|
| Input | 5 | 0 |
| Cache write | 60,494 | 6,049 |
| Cache read | 101,476 | 10,147 |
| **Output** | **14,312** | **1,431** |
| **Total** | **176,287** | **17,628** |

At list rates that is USD 0.787 for ten — **USD 0.0787 per judgement, an effective USD 4.46 per
million.**

**This is a floor.** The ten items were judged from the fields the procedure supplies —
disease, gene, drug — with mechanism filled from model knowledge, which is the circularity the
proposed work removes. A grounded judgement carries quoted evidence in its context and will cost
more. How much more is unmeasured.

**This is why the fan-out rate in section 1 must not be used for judgement work.** That rate,
USD 1.30/M, comes from a workload that was 87.2% cache read and 0.38% output. A judgement writes
a reasoning chain: output is 8.1% of its tokens here, and **output cannot be cached** — it bills
at USD 25/M against cache read's USD 0.50/M. Applying USD 1.30/M to judgement operations
understates them by roughly 3.4x.

The 8,000-token figure used in earlier drafts of the budget was an assumption and was wrong in
both directions: the true total is 17,628 tokens, but the cost per token is what actually
matters, and it is 3.4x higher than assumed.

Items judged: CTBP1/valproic acid, SLC6A17/propranolol, EIF2AK3/glibenclamide, CRPPA/ribitol,
LRRK1/calcitriol, WASHC5/hydroxychloroquine, PDSS1/levocarnitine, SLC19A3/riboflavin,
MEGF10/erlotinib, GHSR/somatropin.

---

### What the grounding pilot found besides prices

These are the reasons the budget grounds every path in full text instead of gating on
structured databases first.

**Databases alone settled 2 of 5 paths.** The three failures each failed differently:

| Item | Why database evidence was not enough |
|---|---|
| LPL / prednisolone | Zero pathway intersection, but a database cannot separate `symptomatic` (a glucocorticoid given for a downstream complication) from `mismatch` |
| FMR1 / mavoglurant | FMR1 has no Reactome pathway membership at all; the only connector was one shared GO term |
| TTPA / vitamin E | Vitamin E has no drug-target record in either database, so the class was assignable only from the pathway name matching the drug name |

The third is the worst case: a label produced by a string coincidence.

**Atoms grounded cleanly.** All four fields for all three genes and all three drugs were
supported by a quoted sentence; zero `ungrounded`. Two findings are worth recording because
they are the kind of thing database annotation does not carry:

- TRMU: *Nucleic Acids Research* 2024 reports most disease variants are **partial**
  loss-of-function. `loss_of_function` alone loses that, and residual activity is what decides
  whether a substrate-supplying drug can work.
- Levacetylleucine: the FDA label states the molecular target is **unknown**, and a 2025
  CLN1-mouse study reports its mechanism "may not address the underlying pathophysiology".
  A model asked to supply mechanism from its own knowledge is likely to call this a
  `causal_match`.

**Database availability is not free.** Throughout the pilot, one MCP endpoint returned
`Rate limit exceeded (global)` on all six attempts and another returned HTTP 500 for the whole
session. The agent reached the same records through the GraphQL and REST APIs directly. At the
proposed volume the workaround has to be budgeted.

---

## 3. Sonnet pricing

Grounding runs on Sonnet, priced from the Opus token profiles above. Published list rates:

| | Opus 5 | Sonnet 5 | Ratio |
|---|---:|---:|---:|
| Input | USD 5.00/M | USD 3.00/M | 0.60 |
| Cache write | USD 6.25/M | USD 3.75/M | 0.60 |
| Output | USD 25.00/M | USD 15.00/M | 0.60 |
| Cache read | USD 0.50/M | USD 0.30/M | 0.60 |

The ratio is 0.60 on all four, so a token profile costs exactly 0.60x on Sonnet whatever its mix.
Gene USD 1.002 → **0.601**, drug USD 0.549 → **0.330**, path USD 0.791 → **0.475**.

**What this does not establish.** It is a price transform, not a quality measurement. Whether
Sonnet reaches the same grounding with the same number of turns is untested; if it needs more
turns the token profile changes and the transform no longer holds. The first 100 units of each
type are run on both models and the agreement published before the second half of any award is
drawn.

---

## 4. The committed core, and the stretch

The proposal commits to a fixed minimum rather than to a coverage figure. The core is the 2,426
existing rows carried to the new standard — grounded, repaired, judged, and measured — with the
500 hand-adjudicated items and all three measurement steps run on them. The 7,884 new items are
what the remaining budget buys, and they are what shrinks if throughput falls short.

| Committed core — 2,426 rows | Units | Passes | Total |
|---|--:|--:|--:|
| Variant-direction grounding | 1,031 | 3 | 1,859 |
| Drug action grounding | 885 | 3 | 876 |
| Database sort | 2,426 | 1 | 1,152 |
| Settled, one confirmation | 970 | 1 | 583 |
| Contested, two readings + exclusion | 1,456 | 3 | 2,625 |
| Grounding verification | 11,086 | 1 | 872 |
| Seven-way judgement + adjudication | 2,426 | 8 | 1,527 |
| Invariance, 2,000 x 12 paraphrases | 2,000 | 36 | 5,666 |
| Rubric ablation, full | 2,426 | 12 | 2,291 |
| Convergence reading, full | 2,426 | 6 | 1,146 |
| **Core subtotal** | | | **18,598** |

| Stretch — 7,884 new items | Units | Passes | Total |
|---|--:|--:|--:|
| Candidate pool construction | 1,031 | 1 | 490 |
| Drug action grounding, new drugs | 2,876 | 3 | 2,847 |
| Database sort | 7,884 | 1 | 3,745 |
| Settled, one confirmation | 3,154 | 1 | 1,896 |
| Contested, two readings + exclusion | 4,730 | 3 | 8,528 |
| Grounding verification | 25,972 | 1 | 2,044 |
| Seven-way judgement + adjudication | 7,884 | 8 | 4,964 |
| Convergence reading, beyond the core | 5,574 | 6 | 2,632 |
| Rubric ablation, beyond the core | 585 | 12 | 552 |
| **Stretch subtotal** | | | **27,698** |

Core plus stretch is USD 46,296, which is the same subtotal as the full ledger in section 5 —
the two tables are the same plan, partitioned. With the 8% reserve of USD 3,704 the request is
USD 50,000. Re-grounding the 2,426 existing rows sits inside the core: it is carried by the
variant-direction, drug-action and sort lines above, not by the separate `Re-ground the 2,426
legacy rows` line, which is the second pass and is what the cap drops.

---

## 5. Ledger — full plan

Every operation the proposal funds, at the prices measured above. Grounding on Sonnet,
judgement and verification on Opus.

### What the USD 50,000 cap buys

| Operation | Units | Passes | Price | Total | Model |
|---|--:|--:|--:|--:|---|
| Candidate pool construction | 1,031 | 1 | 0.475 | 490 | Sonnet |
| Variant-direction grounding | 1,031 | 3 | 0.601 | 1,859 | Sonnet |
| Drug action grounding | 3,761 | 3 | 0.330 | 3,723 | Sonnet |
| Database sort | 10,310 | 1 | 0.475 | 4,897 | Sonnet |
| Settled items, one confirmation | 4,124 | 1 | 0.601 | 2,479 | Sonnet |
| Contested, two full-text readings | 6,186 | 2 | 0.601 | 7,436 | Sonnet |
| Contested, adjacent-class exclusion | 6,186 | 1 | 0.601 | 3,718 | Sonnet |
| Grounding verification | 37,058 | 1 | 0.0787 | 2,916 | Opus |
| Seven-way judgement + adjudication | 10,310 | 8 | 0.0787 | 6,491 | Opus |
| Convergence reading, 8,000 sample | 8,000 | 6 | 0.0787 | 3,778 | Opus |
| Invariance, 2,000 items x 12 paraphrases | 2,000 | 36 | 0.0787 | 5,666 | Opus |
| Rubric ablation, 3,011 sample | 3,011 | 12 | 0.0787 | 2,844 | Opus |
| **Subtotal** | | | | **46,296** | |
| Reserve, 8% | | | | 3,704 | |
| **Total** | | | | **50,000** | |

The verification count is every grounding pass that produced a record: 3,093 + 11,283 + 4,124 +
18,558 = 37,058. The ablation sample is the flex line, sized to what remains under the cap. Per item the capped
plan comes to USD 4.85 (50,000 ÷ 10,310); the as-designed plan to USD 7.21.

### What the work costs as designed

| Operation | Units | Passes | Total |
|---|--:|--:|--:|
| Candidate pool construction | 1,031 | 1 | 490 |
| Variant-direction grounding | 1,031 | 3 | 1,859 |
| Drug action grounding | 3,761 | 3 | 3,723 |
| Database sort | 10,310 | 1 | 4,897 |
| Settled items, two confirmations | 4,124 | 2 | 4,957 |
| Contested, two full-text readings | 6,186 | 2 | 7,436 |
| Contested, all three exclusions | 6,186 | 3 | 11,153 |
| Re-ground the 2,426 legacy rows | 2,426 | 2 | 2,916 |
| Grounding verification | 58,406 | 1 | 4,597 |
| Seven-way judgement + adjudication | 10,310 | 8 | 6,491 |
| Convergence reading, full coverage | 10,310 | 6 | 4,868 |
| Invariance, 2,000 items | 2,000 | 36 | 5,666 |
| Rubric ablation, full coverage | 10,310 | 12 | 9,737 |
| **Subtotal** | | | **68,791** |
| Reserve, 8% | | | 5,503 |
| **Total** | | | **74,294** |

The cap removes USD 24,294: two of the three exclusion classes, the second confirmation on
settled items, re-grounding the legacy rows, and full coverage on ablation and convergence.

### Token forecast

Pass counts times the measured per-pass token totals from section 2:

| | Passes | Tokens each | Total |
|---|--:|--:|--:|
| Gene grounding | 3,093 | 1,373,584 | 4.25B |
| Drug grounding | 11,283 | 623,776 | 7.04B |
| Database sort | 10,310 | 1,227,926 | 12.66B |
| Full-text item passes | 22,682 | 1,373,584 | 31.16B |
| Judgement | 275,670 | 17,628 | 4.86B |
| **Total** | | | **59.97B** |

---

## 6. Derived quantities

| Quantity | Value | How |
|---|--:|---|
| Items | 10,310 | 1,031 audited diseases × 10 candidate drugs — 2,426 existing, 7,884 new |
| Unique drugs | 3,761 | Current set reuses each drug across 2.74 items (2,426 items / 885 unique); 10,310 ÷ 2.74 |
| Judgement operation | USD 0.0787 | **Measured**, ten real items — see section 2. 17,628 tokens each, of which 1,431 are output |

Ten candidates per disease is a design choice, not the present density of 2.35. With only the
drugs that happen to carry a clinical record, `mismatch` — the class the trained model recovers
at 1 of 7 — barely occurs, so candidates have to be selected to populate all four classes and
to include network-close negatives.
