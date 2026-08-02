# Development history

ORPharma has been through fourteen data generations and one backbone change. This page records
what was tried, what failed, and what the failures changed — including the numbers that do not
flatter the project.

All measurements below come from files in this repository or from run outputs kept on the
training machine; where a number has not been independently reproduced, it says so.

---

## The turn that matters

The project began as an **efficacy classifier** — seven verdicts about whether a drug works in a
disease. It became a **mechanism classifier** — four classes about what a drug does relative to
the causal lesion.

The reason was not preference. About 95% of monogenic rare diseases have no approved drug, so
an efficacy label does not exist where it is needed. A mechanism label does, because gene
function and drug target are both public.

| | Efficacy question | Mechanism question |
|---|---|---|
| Asks | does this drug work here | what does this drug do relative to the lesion |
| Needs | a trial | gene function + drug target |
| Available for undrugged disease | no | **yes** |
| Cost | — | the answer is "reaches the lesion", not "will help a patient" |

---

## Generations

| Gen | What it was | What ended it |
|---|---|---|
| v1–v4 | First SFT lines, seven-class efficacy verdicts | Label scheme did not survive contact with undrugged disease |
| v5–v8 | Two-stage SFT, hard-eval holdouts introduced | Evaluation was too easy; the model could pass without mechanism |
| v9 | Five parallel experiments, same day | Merged models published (see [LINKS.md](LINKS.md)) |
| v10 | Redesign | Superseded |
| v11 | Multimodal experiment (protein/molecule encoders) | Not carried forward |
| v12 | Axis-split SFT — drug / disease / source / temporal | Split design kept; data superseded |
| v13 | — | **Never built. Deprecated before training.** |
| v14 | Current backbone line, four-class mechanism labels | Trained; not published |

---

## Backbone selection

Five-fold, disease-level cross-validation, four-class accuracy, 8-bit:

| Backbone | CV accuracy |
|---|---:|
| Qwen3.5-9B | **0.723 ± 0.014** |
| Qwen3.5-4B | 0.643 ± 0.026 |

The 95% intervals do not overlap. Ablation showed the 9B model used the network-proximity and
mechanism-of-action evidence in the prompt while the 4B model did not.

---

## Where the model fails — hard evaluation

A 23-pair adversarial set, built so that roughly a third of the pairs are *close but wrong*:
the drug sits near the causal gene in a network sense, but the mechanism does not connect.

| | Trained (v14) | Base model |
|---|---:|---:|
| Four-class accuracy | **0.565** | 0.304 |
| Binary accuracy | 0.783 | 0.478 |

Training is doing real work — the base model answered `mismatch` for 22 of 23 pairs, which is
how it reached 0.304 without discriminating at all.

**Per-class recall is where the problem is:**

| True class | Recall |
|---|---:|
| `causal_match` | 8/8 — **100%** |
| `symptomatic` | 3/4 — 75% |
| `downstream_match` | 1/4 — 25% |
| **`mismatch`** | **1/7 — 14%** |

Four of the six missed `mismatch` cases were answered `causal_match`. Read together with the
construction of the set, the diagnosis is that the model takes a shortcut: **a causal enzyme
plus a substrate-supplying drug plus zero network hops is read as `causal_match`**, without
checking whether the mechanism actually connects.

**n = 23.** This is a diagnostic, not a benchmark. It is reported because it is the measurement
that exists, and because the failure it names is the one the proposed evaluation is built to
measure at scale.

---

## A negative result we kept

An untrained knowledge-graph node embedding (PrimeKG, 129,375 nodes × 128 dimensions, with 1–3
hop propagation) was added to a disease-held-out ranker as cosine and L2 features.

Dataset: an earlier ranker line, 12,884 labelled pairs across 3,429 diseases. Not the 2,426-row
mechanism set.

| Arm | AUC | EF@10% |
|---|---:|---:|
| Existing features | 0.593 ± 0.019 | 1.337 ± 0.076 |
| + PrimeKG | 0.599 ± 0.015 | 1.337 ± 0.050 |

Paired across 15 folds: AUC +0.006, *p* = 0.193; EF@10% unchanged, *p* = 0.916.

Restricting to the 3,633 rows where both nodes matched, **PrimeKG features alone give AUC
0.531** — near chance. So it is not a coverage-dilution artefact.

What this shows and does not show: it tests an *untrained* embedding reduced to a pairwise
cosine. A cheap method failed. A trained relational GNN is a different object and would need
its own measurement.

Reproduce with [`baselines/`](baselines/); inputs are in `baselines/data/`. Re-run 2026-08-01, figures above reproduced.

---

## The audit that produced the current data

Before any of the above can be evaluated honestly, the clinical record behind each pair has to
be **read**, not matched. All 2,426 rows were read in full text.

| Read outcome | Rows | Share |
|---|---:|---:|
| Approved for this disease | 240 | 9.9% |
| Trial in this disease | 566 | 23.3% |
| Off-label case reports | 23 | 0.9% |
| Preclinical only | 2 | 0.1% |
| **Record exists but is not treatment** | **159** | **6.6%** |
| No record found | 1,436 | 59.2% |

The 6.6% is the finding. An identifier join cannot see it. Breakdown in
[`audit/TRAP_TAXONOMY.md`](audit/TRAP_TAXONOMY.md); the reading procedure and
the trap kinds known at the time of writing are in
[`audit/READING_PROMPT.md`](audit/READING_PROMPT.md).

**The taxonomy has not converged.** New trap kinds were still appearing in the final batch read.
Reported as such.

---

## What is not measured yet

| | |
|---|---|
| Between-judge agreement on the four-class label | **Not measured** on the current set |
| Language-model baselines on the current split | **Not run** |
| Whether the shortcut above persists after hard-negative training | **Not measured** |
| Trap-taxonomy convergence | **Not reached** |

These four are the proposed work.
