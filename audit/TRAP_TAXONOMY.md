# Full-text approval audit — all 2,426 rows

2026-08-01. All 2,426 rows read. The per-row read outcome and the quoted basis text are released
as a six-month deliverable. The instruction used for the read is in
[`audit/READING_PROMPT.md`](READING_PROMPT.md).

Judged by an **agent reading the source text directly**, not by a code join.

---

## 1. How far the drug went in this disease

| | Rows | Share |
|---|---:|---:|
| Approved | 240 | 9.89% |
| Trial | 566 | 23.33% |
| Individual use reports | 23 | 0.95% |
| Preclinical | 2 | 0.08% |
| Not treatment | 159 | 6.55% |
| No record found | 1,436 | 59.19% |
| **Total** | **2,426** | 100% |

Actually given to patients: 829 rows (34.2%).

## 2. Source of the evidence

| | Rows | Share |
|---|---:|---:|
| Not found | 1,379 | 56.84% |
| ChEMBL | 676 | 27.86% |
| ClinicalTrials.gov | 255 | 10.51% |
| Open Targets | 83 | 3.42% |
| Reader's own knowledge | 26 | 1.07% |
| EMA | 7 | 0.29% |

## 3. Checkable identifiers (NCT / EU number)

| Read outcome | Has ref | No ref |
|---|---:|---:|
| Approved | 209 | **31** |
| Trial | 566 | 0 |
| Individual use | 8 | **15** |
| Preclinical | 2 | 0 |
| Not treatment | 159 | 0 |
| Not found | 325 | 1,111 |

Approved 31 + individual use 15 = **46 rows have no identifier to trace back to.**
The 325 "not found" rows that do carry a ref cite it **to show absence** — as in "this NCT is not
a trial of this drug".

## 4. Does the disease carry a record for any drug at all

| Read outcome | Has record | No record |
|---|---:|---:|
| Approved | 209 | 31 |
| Trial | 541 | 25 |
| Individual use | 6 | 17 |
| Preclinical | 2 | 0 |
| Not treatment | 150 | 9 |
| Not found | **358** | **1,078** |
| Total | 1,266 | 1,160 |

`Not found` splits in two — **358 rows** where the disease has other drugs but not this one
(comparable), and **1,078 rows** where the disease itself is absent from the sources
(not comparable).

## 5. How far the drug went in other diseases

| Read outcome | Approved elsewhere | Trial elsewhere | None |
|---|---:|---:|---:|
| Approved | 178 | 45 | 17 |
| Trial | 413 | 128 | 25 |
| Individual use | 21 | 2 | 0 |
| Preclinical | 0 | 0 | 2 |
| Not treatment | 139 | 16 | 4 |
| Not found | **1,242** | 176 | 18 |

Of the 1,436 "not found" rows, **1,242 are drugs already approved in some other disease** — which
is what a repurposing candidate should look like.

## 6. EMA orphan designation

| | Rows | Share |
|---|---:|---:|
| None | 1,589 | 65.50% |
| Designated | 586 | 24.15% |
| Designation withdrawn | 156 | 6.43% |
| Expired | 94 | 3.87% |
| Refused | 1 | 0.04% |

**Withdrawn and expired do not mean development stopped.** Betaine, trientine, lumacaftor,
levofloxacin, miglustat and belzutifan all withdrew the designation while keeping a live marketing
authorisation — sponsors commonly drop orphan status after approval.

---

## 7. The 159 `not treatment` rows — every one read

| Kind | Rows |
|---|---:|
| **A. Right disease, but the drug's role is not treatment** | **105** |
| ├ Conditioning before transplant or gene therapy / immunosuppression / GvHD prophylaxis | 55 |
| ├ Probe substrate in a drug-interaction study (mostly healthy volunteers) | 18 |
| ├ Premedication before infusion (antipyretic, antihistamine, toxicity rescue) | 9 |
| ├ Placebo or comparator arm | 7 |
| ├ Healthy volunteers only | 4 |
| ├ Imaging tracer or contrast agent | 4 |
| └ Diagnostic reagent 2 · background drug in all arms 2 · other 4 | 8 |
| **B. The disease attachment itself is wrong** | **21** |
| ├ `"Fed"` (fed state) → Fish-Eye Disease mis-expansion | 18 |
| └ Fructose intolerance mis-expansion 1 · acquired haemophilia 1 · subtype misattribution 1 | 3 |
| **C. The drug was not in the trial, or a different molecule was** | **7** |
| **D. Trial withdrawn after enrolling zero participants** | **4** |
| **E. A parent-disease record belonging to a different subtype** | **22** |
| **Total** | **159** |

One trial generating many rows is a clear pattern. `NCT00176904` (University of Minnesota bone
marrow transplant) alone produced 6 busulfan rows + 6 cyclophosphamide rows = **12 rows**.
`NCT05981365` (Pfizer voxelotor interaction study, 44 healthy volunteers) turned **7 probe drugs**
into sickle cell disease records.

### Current four-class verdicts on those 159 `not_treatment` rows

| Verdict | Rows |
|---|---:|
| mismatch | 94 |
| symptomatic | 38 |
| downstream_match | 21 |
| causal_match | 6 |

**65 rows are not treatment yet are not labelled mismatch.** They fall under the Step 0
procedural-drug rule in rubric v9.2, which has not been applied to them yet.

---

## 8. Composition by source

Rows carry the source they were drawn from. One source dominates the failure mode above: the
ChEMBL-clinical-record line has evidence at 75.8%, and in exchange **137 of the 159
`not_treatment` rows are concentrated there** — because "a drug that reached a clinical phase in
ChEMBL" was taken as a positive as-is. That table records only that the drug appeared in a
trial; **it does not record what the drug was there to do.**

Sources built as wrong answers for evaluation carry almost no clinical record. That is by
design, not a defect. Per-row source labels ship with the release.



---

## 9. Rows needing repair — 121 after removing overlap

| What | Rows | Why |
|---|---:|---|
| Not treatment, yet the verdict is not mismatch | 65 | Procedural-drug rule not applied |
| Approved or individual-use rows with no identifier to trace | 46 | Cannot be verified |
| Reader's own knowledge is the only basis | 26 | No source. 12 of them have an empty `basis` too |
| **Total after removing overlap** | **121** | |
