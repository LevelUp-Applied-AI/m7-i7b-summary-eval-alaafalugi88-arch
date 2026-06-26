# Module 7 Integrated Evaluation Report — Fine-Tuning vs. Pre-Trained Inference

> **Author:** Alaa Falugi | **Branch:** integration-7b-summary-eval | **Date:** June 2026

---

## 1. Comparison Table

| Task | Approach | Model | Training cost | Inference cost | Quality metric | Value |
|---|---|---|---|---|---|---|
| Sentiment classification (Lab 7A) | Fine-tuning | `distilbert-base-uncased` | ~20 min CPU · 5,977 labeled examples · 2 epochs | ~50 ms / example | Macro-F1 | **0.6298** |
| Domain transfer (Integration 7A) | Fine-tuned model out-of-domain | (same checkpoint) | already trained | ~50 ms / example | Domain-shift judgment | Visible degradation — app-review vocabulary absent from tech news; neutral class inflated |
| Extractive QA (Lab 7B) | Pre-trained inference | `distilbert-base-cased-distilled-squad` | 0 | ~50 ms / example | EM / token-F1 | **EM 0.344 / F1 0.461** |
| Summarization (Integration 7B) | Pre-trained inference | `sshleifer/distilbart-cnn-6-6` | 0 | ~4.8 sec / example | ROUGE-1 / 2 / L F1 | **ROUGE-1 0.3201 / ROUGE-2 0.1207 / ROUGE-L 0.2241** |
| Speech-to-text (Tier 1) | Pre-trained inference | `openai/whisper-tiny.en` | 0 | ~5 sec / 10-sec clip | Corpus WER | **0.1017** |

---

## 2. Findings

(ابقيها كما هي — جيدة)

---

## 7. Challenge Extensions

### 7.1 — Cross-Modal Observation (Tier 1)

(ابقيها كما هي)

---

### 7.2 — Multi-Model Production Selection (Tier 3)

**Candidate models evaluated on 120 tech-news articles**

| Model                              | ROUGE-1 | ROUGE-2 | ROUGE-L | Mean latency (s) | Disk (MB) |
|------------------------------------|---------|---------|---------|------------------|-----------|
| `sshleifer/distilbart-cnn-6-6` (baseline) | 0.3201 | 0.1207 | 0.2241 | 4.80 | ~250 |
| `t5-small`                         | 0.3201 | 0.1207 | 0.2241 | 5.22 | ~250 |
| `sshleifer/distilbart-xsum-12-1`   | 0.2460 | 0.0577 | 0.1721 | 16.31 | ~443 |
| `sshleifer/distilbart-cnn-12-6`    | **0.3889** | **0.1780** | **0.2846** | 13.93 | ~1220 |

**Pareto frontier analysis**  
`distilbart-cnn-6-6` and `distilbart-cnn-12-6` are the only **Pareto-optimal** models.  
`t5-small` and `distilbart-xsum-12-1` are **Pareto-dominated**.

**Production recommendations**

| Scenario | Recommended model | Justification |
|----------|-------------------|-------------|
| **Batch backend** (latency tolerant, quality maximized) | `sshleifer/distilbart-cnn-12-6` | Highest ROUGE-L (0.2846) while maintaining acceptable latency for overnight processing. |
| **Real-time / near real-time API** (latency budget ≤ 8s) | `sshleifer/distilbart-cnn-6-6` | Best speed-quality trade-off (4.8s latency with solid ROUGE scores). |

**Quality floor:** Any model with **ROUGE-L < 0.20** is rejected regardless of latency (e.g. xsum model).  

**Pareto-dominated models (drop from future consideration):** `t5-small` and `sshleifer/distilbart-xsum-12-1`.

**Visualization:** See `model_pareto.png` for the full scatter plot with Pareto frontier line.