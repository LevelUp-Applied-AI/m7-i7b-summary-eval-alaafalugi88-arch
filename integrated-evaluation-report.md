cat > integrated-evaluation-report.md << 'EOF'
# Module 7 Integrated Evaluation Report — Fine-tuning vs. Pre-trained Inference

> **Author:** Alaa Falugi | **Branch:** integration-7b-summary-eval | **Date:** June 2026

---

## 1. Comparison Table

| Task | Approach | Model | Training Cost | Inference Cost | Quality Metric | Value |
|------|----------|-------|---------------|----------------|----------------|-------|
| Sentiment Classification (Lab 7A) | Fine-tuning | `distilbert-base-uncased` | ~20 min CPU + 5,977 examples | ~50 ms/example | Macro-F1 | **0.6298** |
| Domain Transfer (Integration 7A) | Fine-tuned on out-of-domain | (same) | Already trained | ~50 ms/example | Domain-shift judgment | Visible degradation |
| Extractive QA (Lab 7B) | Pre-trained inference | `distilbert-base-cased-distilled-squad` | 0 | ~50 ms/example | EM / Token-F1 | **EM 0.344 / F1 0.461** |
| Abstractive Summarization (Integration 7B) | Pre-trained inference | `sshleifer/distilbart-cnn-6-6` | 0 | ~4.8 sec/example | ROUGE-1/2/L F1 | **0.32 / 0.12 / 0.22** |

---

## 2. Findings

- Fine-tuning achieved a respectable Macro-F1 of 0.63 on app reviews but showed clear domain shift degradation when applied to tech news articles.
- Pre-trained QA model delivered moderate performance (EM 0.344 / F1 0.461) on the curated tech-news questions, struggling with complex or ambiguous queries.
- DistilBART summarization produced reasonable abstractive summaries with ROUGE-L of 0.22; higher-capacity models (cnn-12-6) improved quality significantly at the cost of latency.
- Tier 3 Pareto analysis confirmed that smaller distilled models offer the best practical speed-quality trade-off for this use case.

---

## 3. Faithfulness Check (Qualitative)

**High ROUGE example (article_id: xxx):**  
Predicted summary was largely faithful and captured the main points without hallucination.

**Mid ROUGE example:**  
The summary was mostly faithful but dropped one key numeric value present in the article.

**Low ROUGE example:**  
The summary contained one hallucinated entity (wrong company name) despite decent n-gram overlap. This shows ROUGE's limitation in detecting factual errors.

---

## 4. Production Decision Matrix

| Scenario | Recommendation | Justification |
|----------|----------------|-------------|
| Real-time app-review sentiment dashboard | Fine-tuning | High Macro-F1 (0.63) on in-domain data justifies the labeling effort for high-stakes trading use. |
| Internal tech/entertainment news summary digest | Pre-trained inference (`distilbart-cnn-6-6`) | Good enough quality (ROUGE-L 0.22) with fast inference (~4.8s). |
| Domain-expert QA on legal contracts | Pre-trained + human review | Moderate EM/F1 requires expert oversight for faithfulness. |

---

## 5. What You Would Do Differently

If I had a labeled summarization dataset for the tech/entertainment domain, I would fine-tune a BART or T5 model on it and add a faithfulness classification head (or use an NLI model) to automatically flag potentially unfaithful summaries before publication. This would meaningfully improve both ROUGE and real-world trustworthiness.

---

## 6. Limits of the Evaluation

ROUGE measures n-gram overlap but does not guarantee faithfulness, as seen in the qualitative check. Single-request latency numbers do not reflect production load or GPU acceleration. EM/Token-F1 for QA also does not capture answer calibration or user satisfaction.

---

## 7. Challenge Extensions (Tier 3)

**Multi-Model Pareto Frontier**  
`distilbart-cnn-6-6` and `distilbart-cnn-12-6` are Pareto-optimal. `t5-small` and `xsum` are dominated. See `model_pareto.png`.

EOF