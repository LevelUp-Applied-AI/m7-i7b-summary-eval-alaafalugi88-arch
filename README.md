# Module 7 Week B — Integration Task: Summarization & Integrated Evaluation Report

This is the starter repo for the Module 7 Week B Integration Task. **The integrated evaluation report you produce here is the M7 deliverable.**

The full integration guide is at <a href="https://levelup-applied-ai.github.io/aispire-14005-pages/modules/module-7/496c1c2b" target="_blank">the integration guide page</a> — read it first.

## Quick start

```bash
pip install -r requirements.txt
make summarize    # runs full pipeline; first run downloads ~250 MB
```

The first call to `pipeline("summarization", ...)` downloads the model. Plan ~3 minutes for the first run; subsequent runs use cached weights. The full evaluation on 120 articles completes in ~6–8 minutes on CPU after the model is cached.

## What you will produce

Committed:
- `summarize.py` — your implementation
- Updated `README.md` — 1–2 paragraphs documenting model id, corpus version, re-run command (this section is the template; replace it)
- `summary_predictions.csv` — 120 rows with reference, predicted, and per-summary ROUGE
- `summary_metrics.json` — aggregate ROUGE-1/2/L F1
- `integrated-evaluation-report.md` — six-section integrated report (the M7 deliverable). Includes an optional Section 7 (Challenge Extensions) for learners completing challenge tiers — see the integration's learner guide.

**No model file** — pre-trained model loads from Hugging Face Hub at runtime.

## Data

- `data/tech_news_articles.csv` — 1,033 tech / entertainment / digital-culture news articles, curated from <a href="https://huggingface.co/datasets/glnmario/news-qa-summarization" target="_blank">glnmario/news-qa-summarization</a>. The full pool is here for inspection and stretch use; the integration evaluates on the 120-article subset that has reference summaries.
- `data/tech_news_summaries_reference.csv` — 120 reference summaries (one per evaluated article), shipped with the curated dataset (CNN editor-authored summaries from the source dataset).
- `data/tiny_articles_smoke.csv` + `data/tiny_refs_smoke.csv` — 3-row CI smoke fixtures (articles and references in separate files, matching the real-data schema).

## Make targets

```bash
make summarize    # full pipeline against the 120-article evaluation set
make smoke        # CI-only target — 3-row fixture
make clean        # remove generated outputs
```

## Summarization model

The default model is **`sshleifer/distilbart-cnn-6-6`** — a distilled version of Facebook's BART encoder–decoder transformer, fine-tuned on the CNN/DailyMail abstractive summarization corpus. The `6-6` suffix denotes 6 encoder layers and 6 decoder layers, making it roughly half the size of BART-large-CNN while retaining strong news-summarization quality. The model weights (~250 MB) are downloaded from Hugging Face Hub on the first run and cached locally; no model file is committed to this repo. To use a different model, set the `SUMM_MODEL_FOR_CI` environment variable before running `make summarize`.

## Corpus and re-run

The evaluation runs over **120 tech/entertainment news articles** drawn from the `glnmario/news-qa-summarization` dataset (Module 6 corpus), stored in `data/tech_news_articles.csv`. Reference summaries are CNN editor-authored single-sentence ledes in `data/tech_news_summaries_reference.csv`. To reproduce the full evaluation from scratch:

```bash
make summarize
```

This generates `summary_predictions.csv` (120 rows with reference, predicted, and per-article ROUGE) and `summary_metrics.json` (aggregate ROUGE-1/2/L F1, article count, and model id).

## Submission

Open a Pull Request from your working branch into `main`. The autograder runs `make smoke` against the 3-row fixture and validates artifact schemas. PR description requirements are in the integration guide.

---

## License

This repository is provided for educational use only. See [LICENSE](LICENSE) for terms.

You may clone and modify this repository for personal learning and practice, and reference code you wrote here in your professional portfolio. Redistribution outside this course is not permitted.



## Summarization Evaluation (Integration 7B)

We used the pre-trained summarization model **`sshleifer/distilbart-cnn-6-6`** (a distilled BART model fine-tuned on CNN/DailyMail news summarization dataset). This model was chosen as the baseline due to its good balance between quality and inference speed on CPU.

**Corpus**: 120 tech and entertainment news articles from Module 6, paired with human-written reference summaries (`data/tech_news_summaries_reference.csv`).

**Reproduce the full evaluation**:
```bash
make summarize

This command runs the complete pipeline on all 120 articles and generates:

summary_predictions.csv
summary_metrics.json

Tier 3 (Pareto Frontier): Run python model_comparison.py (or individually via python summarize.py --model <model_id>) to compare 4 models and generate model_comparison.csv + model_pareto.png.

Model Comparison Results (Tier 3)



































ModelROUGE-LMean Latency (s)Statusdistilbart-cnn-6-60.22414.80Pareto-optimalt5-small0.22415.22Dominateddistilbart-xsum-12-10.172116.31Dominateddistilbart-cnn-12-60.284613.93Pareto-optimal
Best overall choice depends on the scenario: distilbart-cnn-6-6 for speed, distilbart-cnn-12-6 for maximum quality.
text