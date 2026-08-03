# ORPharma — Mechanism-Grounded Evaluation for Rare Disease Drug Repurposing

About 95% of monogenic rare diseases have no approved drug. That removes the supervision
signal most repurposing systems rely on — *is this drug approved for this disease* — precisely
where it is needed.

This repository holds the method artefacts for an evaluation that asks a different question:
**not whether a drug works, but why it would.**

Work in progress. The evaluation set itself is not published yet; see
[Status](#status) for what exists and what does not.

---

## The four-class relation

Given a `(disease, causal gene, candidate drug)` triple, classify the mechanistic relation:

| Class | Meaning |
|---|---|
| `causal_match` | The drug acts on the lesion itself, or supplies what the lesion fails to produce |
| `downstream_match` | The drug acts on a step that the lesion drives, without restoring the lesion |
| `symptomatic` | The drug acts on a state reached from many causes, for the same reason it would be given in any of them |
| `mismatch` | No mechanistic contact with the lesion or anything it drives |
| `unknown_action` | The answer would flip depending on information the input does not carry |

Gene function and drug target are both public, so this label exists even where no trial does.

The judging procedure is a gate on variant direction, a rule that removes procedural agents,
then two ordered tests. It is written as prose sentences rather than a scoring function on
purpose: every boundary that moved between versions moved because a sentence was ambiguous, not
because a weight was wrong. The procedure is released with the evaluation set.

## Why not train on approval status

Knowledge-graph systems typically learn from approved `treats` edges. Two consequences follow.

The label collapses **disease-modifying** and **symptomatic** into one positive class. A drug
approved for a disease may be doing nothing to the lesion.

And the model learns **network proximity**, which is not the same as mechanism. A held-out
evaluation that does not hold out whole diseases cannot tell the two apart.

## How the 2,426 rows were assembled

The set was built, not inherited: merged and deduplicated from eight source files, each row
carrying the basis on which it was drawn — clinical record, hard negative, contrast pair,
treatabolome entry, or designer-set distractor. The per-row basis ships with the release.

### Normalisation

| Entity | Vocabulary | Coverage |
|---|---|--:|
| Disease | **Mondo** | 2,412 / 2,426 (99.4%) |
| Disease | OMIM | 22 (0.9%) |
| Causal gene | **HGNC** | 2,425 / 2,426 (100%) |
| Drug | **ChEMBL** | 2,307 / 2,426 (95.1%) |
| Drug target protein | **UniProt** | every row, 3,513 accessions across up to nine targets per drug |
| Network proximity | STRING, Guney z-score | 373 (15.4%) |

Upstream sources behind those vocabularies: ChEMBL drug indications, ClinicalTrials.gov,
Open Targets, Orphanet, the Treatabolome, and STRING for the network features.

About 38% of rows — the ChEMBL clinical, real-positive and Treatabolome strata — were drawn
because a clinical record exists. The rest are hard negatives, decoys and contrast pairs,
selected so that all four classes are populated. The full-text audit found no record for 1,436
rows (59.2%), and 159 rows whose record exists but is not treatment.

**The source labels are themselves LLM output.** `verdict`, `logic_class` and `reasoning` in
those eight files were assigned by a model, not by a human panel — the only exception being 8
designer-set distractors in `eval_gold_23.jsonl`. They are treated as prior material, not as
ground truth, which is part of why the proposed work re-grounds and re-judges the set.

## Reading the evidence instead of joining identifiers

Before any of this can be evaluated, the clinical record behind each pair has to be read, not
matched. Joining identifiers cannot distinguish three cases that look identical to a query:

- a drug with real evidence in this disease,
- a drug with no evidence,
- a drug whose record exists but **is not treatment at all**.

The third kind was **6.6%** of rows in a full-text audit of 2,426 pairs. Examples found:

| Kind | Case |
|---|---|
| Transplant conditioning | One bone-marrow-transplant protocol generated 12 rows — busulfan and cyclophosphamide across six different lysosomal diseases. The transplant is the treatment; the drugs are tools |
| Identifier mis-expansion | A database expanded the trial-condition string `"Fed"` (fed-state bioequivalence) into *Fish-Eye Disease*, producing 18 spurious phase-1 rows for antihistamines and antipsychotics |
| Probe substrate | One drug-drug-interaction study in 44 healthy volunteers produced 7 sickle-cell "indication" rows |
| Placebo arm | Sodium chloride recorded as a phase-3 indication |
| Wrong etiology | An *acquired* autoantibody disease filed under the inherited gene's term |

**Not all of these are repaired.** Of the 159 rows found not to be treatment, 94 carry a
`mismatch` verdict and **65 still carry something else** — 38 `symptomatic`, 21
`downstream_match`, 6 `causal_match`. Rubric v9.2 has a clause that covers them; it has not been
applied to those rows yet.

The reading prompt, including the trap kinds known at the time of writing, is in
[`audit/READING_PROMPT.md`](audit/READING_PROMPT.md). The taxonomy that came out of the audit is
in [`audit/TRAP_TAXONOMY.md`](audit/TRAP_TAXONOMY.md).

**The taxonomy has not converged.** New trap kinds were still appearing in the final batch of
rows read. That is reported here rather than smoothed over, because a completeness claim would
be false.

## A negative result we are keeping

An untrained knowledge-graph node embedding (PrimeKG, 129,375 nodes × 128 dims, with 1–3 hop
propagation) was added to a disease-held-out ranker as cosine and L2 features.

| Arm | AUC | EF@10% |
|---|---:|---:|
| Existing features | 0.593 ± 0.019 | 1.337 ± 0.076 |
| + PrimeKG | 0.599 ± 0.015 | 1.337 ± 0.050 |

Paired across 15 folds: AUC +0.006, *p* = 0.193. EF@10% unchanged, *p* = 0.916.

Restricting to the 3,633 rows where both nodes matched, **PrimeKG features alone give AUC
0.531** — near chance. So this is not a coverage-dilution artefact.

What this does and does not show: it tests an *untrained* embedding reduced to a pairwise
cosine. It says a cheap method failed. It does not say the knowledge-graph route is wrong —
a trained relational GNN is a different object and would need its own measurement.

Reproduce with [`baselines/`](baselines/) — the scripts and their input tables both ship here
(Python, LightGBM, scikit-learn):

```
python baselines/eval_primekg_only.py
```

Re-run 2026-08-01: PrimeKG-only **0.531 ± 0.022**, existing features **0.593 ± 0.024**, both
**0.597 ± 0.023**, on the 3,633 matched rows across 1,061 diseases.

## Status

| | |
|---|---|
| Four-class rubric | v9.2, locked |
| Triples | 2,426 across 1,031 monogenic diseases; 1,022 of them carry a MONDO identifier |
| Full-text evidence audit | Complete — 2,426 / 2,426 |
| Format sample | [`data/sample_30.csv`](data/sample_30.csv) — 27 rows, all six read outcomes |
| **Evaluation set release** | **Not yet** — planned as a six-month deliverable |
| Between-judge agreement | **Not yet measured** |
| Language-model baselines | **Not yet run on this split** |

Rows whose evidence rests on model knowledge rather than a source are flagged rather than
dropped; in the full-text read that is **26 of 2,426** (`source: model_knowledge`), 12 of which
carry no basis text either. Of the full set, 52% of rows carry some checkable trial identifier
and 32% carry one for an approval or a trial in that same disease.

## Measured costs

[`pilot/COSTS.md`](pilot/COSTS.md) holds the token counts and per-unit prices behind this work:
the fan-out rate for the project, a grounding pilot on three genes, three drugs and five items,
and a judgement pilot on ten items run through the rubric. Grounding and judgement are priced
separately — a judgement writes a reasoning chain, and output cannot be cached, so it costs
**3.4x** what the project's cached fan-out average would suggest. The grounding pilot also
records that structured databases alone settled 2 of 5 mechanistic paths, each failure for a
different reason.

## Contact

`aiscience` correspondence and questions: open an issue.

## License

This repository carries two licences.

| Scope | Licence |
|---|---|
| Source code — `baselines/` and any other code | [Apache-2.0](LICENSE) |
| Data and methodology — `data/`, `audit/`, `pilot/`, and the Markdown documents | [CC BY 4.0](LICENSE-DATA) |

Both permit commercial use. Attribution is required for the data and methodology.

Suggested citation:

> ORPharma, Foundation19 (2026). Rare-disease drug repurposing judgement criteria and
> labelled samples. https://github.com/Foundation19/orpharma
