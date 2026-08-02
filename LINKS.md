# Published artefacts

Links verified live on 2026-08-01. Anything not listed here is not published.

## Models — Hugging Face

Full merged models, not adapters. Base: `Qwen/Qwen3.5-9B`.

| Model | Params | Published |
|---|---:|---|
| [orpharma-v9-exp1-merged](https://hf.co/Misopa/orpharma-v9-exp1-merged) | 9.41B | 2026-05-21 |
| [orpharma-v9-exp2-merged](https://hf.co/Misopa/orpharma-v9-exp2-merged) | 9.41B | 2026-05-21 |
| [orpharma-v9-exp3-merged](https://hf.co/Misopa/orpharma-v9-exp3-merged) | 9.41B | 2026-05-21 |
| [orpharma-v9-exp4-merged](https://hf.co/Misopa/orpharma-v9-exp4-merged) | 9.41B | 2026-05-21 |
| [orpharma-v9-exp5-merged](https://hf.co/Misopa/orpharma-v9-exp5-merged) | 9.41B | 2026-05-21 |
| [orpharma-v10-merged](https://hf.co/Misopa/orpharma-v10-merged) | 9.65B | 2026-06-21 |

`exp1`–`exp5` are five training-condition variants released the same day, not five checkpoints
of one run. `v10` is a later line.

**Model cards are thin.** These were published as run artefacts rather than as products, and the
`image-text-to-text` task tag some of them carry is a metadata artefact of the training
framework — the models classify text. Treat [HISTORY.md](HISTORY.md) as the description.

## Datasets — Hugging Face

| Dataset | Contents |
|---|---|
| [orpharma-v8-eval-results](https://hf.co/datasets/Misopa/orpharma-v8-eval-results) | v8 evaluation outputs |

## Not published

| | Why |
|---|---|
| v14 backbone adapter | Trained, kept on the training machine. Not uploaded |
| The 2,426-row mechanism set | Planned as a six-month deliverable, released through Monarch |
| Training data for v5–v12 | Format and label scheme differ by generation; superseded |
| Evaluation answer keys | Publishing them would retire the evaluations they belong to |
