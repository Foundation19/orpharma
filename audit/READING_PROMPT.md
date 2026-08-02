> The prompt below is reproduced as it was run. Paths such as `data/drugdb/raw/…` point into
> the working tree, not into this repository. The underlying sources are public: ChEMBL drug
> indications, ClinicalTrials.gov, Open Targets, and EMA orphan designations.

For each (disease, gene, drug) triple in the input, find out how far this drug has gone — in this
disease and elsewhere — by opening the source files yourself.

Input:  ./chunks/c_NN.json
        (fields: row, disease, gene_symbol, candidate_drug — nothing else)
Output: ./out/c_NN.jsonl
        One JSON object per line, same order, one line per input case.

Do not read any other file under data/master/. Do not use the web.

## Sources — search these yourself

  data/drugdb/raw/chembl_drug_indication.jsonl
      60,055 lines, one JSON per line.
      Fields: molecule_chembl_id, parent_molecule_chembl_id, efo_id, efo_term, mesh_heading,
              max_phase_for_ind, indication_refs.
      efo_id mixes vocabularies — MONDO:, EFO:, Orphanet:, HP:, MESH:.
      A drug's records may sit on a salt ID or on the parent ID. Follow parent_molecule_chembl_id
      in both directions before concluding a drug has no record.

  data/drugdb/raw/ema_orphan_designations.xlsx
      Columns: Medicine name, Related EMA product number, Active substance,
               Date of designation / refusal, Intended use, EU designation number, Status.

  data/drugdb/raw/opentargets_26.06/drug_molecule.parquet
      name / synonym / tradeName index. Use it to resolve a drug name to a ChEMBL ID.
      **Match on the `name` field only.** The synonym and tradeName lists are contaminated:
      "sirolimus" also returns everolimus, "atorvastatin" returns simvastatin and rosuvastatin,
      "dexamethasone" returns prednisolone and prednisone, "clarithromycin" returns azithromycin,
      "morphine" returns fentanyl, "metformin" returns rosiglitazone. A synonym hit is not
      identification.
      `description` and `maximumClinicalStage` here sometimes carry an approval the two indication
      tables do not — sacrosidase's only approval evidence sits there. Read them, but corroborate
      before relying on them; they also carry claims that are simply wrong.

  data/drugdb/raw/opentargets_26.06/clinical_indication.parquet
      drugId, diseaseId, maxClinicalStage.

  ClinicalTrials.gov MCP tools, when you need to check what a cited NCT actually studied.

**Do not use `data/drugdb/work/axis_drug*.jsonl`.** That mapping is wrong — 103 of its 185
`ot_synonym` entries point at a different molecule (adalimumab→infliximab,
atorvastatin→simvastatin, tobramycin→dexamethasone, sirolimus→everolimus). Resolve drug names
yourself.

## How to decide

Match by **reading the disease names**, not by matching identifiers. `Fish-eye disease` and
`fish eye disease` are the same disease whatever ID each source uses.

A drug approved for a broader indication that contains this disease counts as approved for it —
sodium phenylbutyrate is approved for "urea cycle disorders", and citrullinemia type I is one of
them. A drug approved for a broad clinical category does not — a drug approved for "epilepsy" is
not approved for a specific epileptic encephalopathy, and one approved for "hypertrophic
cardiomyopathy" is not approved for a named genetic subtype. When you use a broader term, name it
in `note` so the reader can reverse the call.

## Records that are in the source but are not treatment of the disease

These are known to be present. When you hit one, record `phase_this_disease` as `"not_treatment"`
and say which kind it is in `note`.

  - **Identifier mis-expansion.** ChEMBL has expanded the trial-condition string `"Fed"` into
    `Fish-Eye Disease` (Orphanet:79292), producing ~20 phase-1 rows for drugs like lamotrigine and
    ondansetron. Their cited NCTs are healthy-volunteer bioequivalence studies. Other
    abbreviation collisions may exist — if a phase-1 record looks implausible, open the NCT.
  - **Probe substrate.** A drug can appear in a trial only as a probe — pharmacokinetic
    (midazolam for CYP3A4, itraconazole as CYP3A inhibitor, celecoxib for CYP2C9) or
    pharmacodynamic (oxypurinol infused to measure xanthine-oxidase-derived superoxide).
    ChEMBL then tags it with the sponsor's disease. One DDI cocktail study produced six such rows
    for sickle cell anaemia in a single chunk. Open the NCT and read what the drug's role was.
  - **Healthy volunteers under a disease tag.** A phase-1 study can be registered under the
    sponsor's intended indication while enrolling only healthy adults. No identifier collision is
    involved — the tag is deliberate — but no patient received the drug. Check
    `healthy_volunteers` and the enrolled population, not just the condition field.
  - **Given to every arm.** Chlorhexidine appears as a cystic fibrosis record because it is the
    skin cleanser both arms receive in an inhaled-vancomycin trial. The same NCT supports a
    genuine `trial` verdict for the actual study drug — so one reference can mean opposite things
    for two drugs.
  - **Toxicity rescue.** Leucovorin alongside pyrimethamine, mesna alongside cyclophosphamide,
    phenytoin as seizure cover during busulfan conditioning. These have no endpoint of their own.
  - **The wrong etiology under the right name.** A trial of *acquired* haemophilia A (autoantibody
    to factor VIII) filed under the inherited `hemophilia A` term. The disease name matches; the
    disease does not. Watch for acquired phenocopies generally.
  - **A class record standing in for one molecule.** ChEMBL's `CANNABINOL` entry collects
    cannabinoid-class trials — its Huntington row cites a THC + cannabidiol study in which
    cannabinol was never given.
  - **Procedure-only drug.** Conditioning before transplant or gene therapy (busulfan,
    cyclophosphamide, treosulfan, melphalan, thiotepa), graft immunosuppression (mycophenolate,
    tacrolimus), premedication, imaging tracers.
  - **Placebo or comparator arm.** Sodium chloride and similar appearing as a disease indication.
  - **Not a drug name.** Some inputs are class or combination strings
    ("ACE inhibitor + diuretic", "Antiepileptic (levetiracetam or valproate)"). Resolve a
    representative member and say which one you used.

This list came from reading 350 rows and is **not** exhaustive — nine further kinds turned up after
it was written, and they kept appearing in the last chunk read. Expect kinds not listed here. If you
find one, say so in `note` and start that note with `NEW TYPE:`. Finding a new kind is a normal
result, not a failure.

The list is a starting point, not a filter. Decide from what the record actually says, not from
whether it matches something above.

## Two more places the same failure appears

The traps above are all disease-side — the wrong disease got attached to a real record. The same
thing happens on the drug side and in the other source file:

  - **The cited trial does not contain this drug.** ChEMBL gives fiboflapon a cystic fibrosis row
    citing a trial whose only interventions are glutathione and saline. Open the trial and check the
    intervention list names your drug.
  - **A precursor or analogue was the one studied.** Niacinamide's ataxia-telangiectasia rows cite
    nicotinamide riboside trials — a different molecule.
  - **Open Targets has its own bad rows.** `clinical_indication.parquet` records berotralstat as
    approved for Alzheimer disease, and the CFTR modulators as approved for acute lung injury.
    Neither exists in ChEMBL. Treat an OT-only claim with the same suspicion as a ChEMBL-only one.
  - **One label can produce several indications.** A single DailyMed setid generated three separate
    phase-4 rows for trientine (rheumatoid arthritis, biliary cirrhosis, Wilson disease); only
    Wilson disease is authorised.
  - **`max_phase 4.0` can bleed from a parent disease to a subtype.** Eliglustat shows 4.0 for
    Gaucher type 3 while the authorisation covers type 1 only.

## Output keys — exactly these

  row                          unchanged

  phase_this_disease           "approved" | "trial" | "off_label_case" | "preclinical" |
                               "not_treatment" | "not_found"

  phase_other_disease          how far this drug has gone in any other disease:
                               "approved" | "trial" | "none"

  ema_status                   "positive" | "expired" | "withdrawn" | "negative" | "none"
                               Record the Status field as it stands. Do not infer approval or
                               non-approval from it.
                               `Withdrawn` means the designation was withdrawn — nothing more.
                               It does NOT mean development stopped: betaine, trientine,
                               lumacaftor, levofloxacin, miglustat and belzutifan all carry a
                               Withdrawn designation alongside a live marketing authorisation
                               (sponsors often drop orphan status after approval). `Expired`
                               likewise says only that the term lapsed.
                               If a Withdrawn or Expired designation sits next to an approval you
                               found elsewhere, say so in `note`.
                               The designation belongs to the substance, not the disease. If the
                               substance holds several, record the one whose Intended use is
                               closest to this disease and list the others in note; if none
                               relates to this disease, say that in note.
                               Check whether the designation is held by a different molecule than
                               the input drug — arbaclofen is not baclofen, ubiquinol is not
                               ubidecarenone, gallium citrate is not gallium nitrate. Some
                               designations are filed under a chemical name rather than the drug
                               name and will not be found by a name search; searching the
                               Intended-use disease text finds those.

  disease_has_any_drug_record  "yes" | "no" — does this disease appear anywhere in the sources for
                               any drug at all. A "no" here means the row cannot discriminate.

  basis                        the exact line or field value you based phase_this_disease on,
                               quoted from the source. Empty string only when you found nothing.

  source                       "chembl" | "ema" | "ot" | "ctgov" | "not_found_in_sources" |
                               "model_knowledge"
                               Use "not_found_in_sources" when your searches returned nothing.
                               Use "model_knowledge" only when you are answering from your own
                               knowledge rather than from a source. Do not conflate the two.

  ref                          checkable identifier (NCT…, EU/3/…) or ""

  note                         what a reader needs to know about this row: which broader term you
                               used, which trap kind you hit, which representative drug you
                               resolved, or why the case is ambiguous. Empty string if none.

## Working files

You may write helper scripts into the scratchpad directory. **Do not delete or rename anything.**
No `rm`, no `mv`, no `sed -i`. If a helper script needs changing, write a new file with a new
name and use that one. Leftover files are fine and will be cleaned up later.

## Rules

- Never take an identifier out of a sentence without reading the sentence. A sentence can cite an
  NCT number in order to say that no trial of this drug exists.
- A record existing in ChEMBL is not by itself evidence of treatment. Read what the record is.
- If your searches return nothing, that is `not_found` with source `not_found_in_sources` —
  not `model_knowledge`, and not an assertion that nothing exists.
- Quote in `basis`. A verdict with an empty `basis` and a source other than
  `not_found_in_sources` will be treated as unverified.

Your final text output should be only the number of lines written, followed by anything you found
that the person reading this should know — especially anything you marked `NEW TYPE:`.
