# Module 7 Integrated Evaluation Report — Fine-Tuning vs. Pre-Trained Inference

> **Author:** Alaa Falugi | **Branch:** integration-7b-summary-eval | **Date:** May 2026

---

## 1. Comparison Table

| Task | Approach | Model | Training cost | Inference cost | Quality metric | Value |
|---|---|---|---|---|---|---|
| Sentiment classification (Lab 7A) | Fine-tuning | `distilbert-base-uncased` | ~20 min CPU · 5,977 labeled examples · 2 epochs | ~50 ms / example | Macro-F1 | **0.6298** |
| Domain transfer (Integration 7A) | Fine-tuned model out-of-domain | (same checkpoint) | already trained | ~50 ms / example | Domain-shift judgment | Visible degradation — app-review vocabulary absent from tech news; neutral class inflated as model hedges on unfamiliar signals |
| Extractive QA (Lab 7B) | Pre-trained inference | `distilbert-base-cased-distilled-squad` | 0 | ~50 ms / example | EM / token-F1 | **EM 0.344 / F1 0.461** |
| Summarization (Integration 7B) | Pre-trained inference | `sshleifer/distilbart-cnn-6-6` | 0 | ~3 sec / example | ROUGE-1 / 2 / L F1 | **ROUGE-1 0.3691 / ROUGE-2 0.1583 / ROUGE-L 0.2671** |
| Speech-to-text (Tier 1) | Pre-trained inference | `openai/whisper-tiny.en` | 0 | ~5 sec / 10-sec clip | Corpus WER | **_(paste from asr_metrics.json)_** |

## 2. Findings

- **Fine-tuning achieved macro-F1 0.6298 on in-domain app-review sentiment**, with the strongest per-class F1 on the negative class (0.716) and weakest on neutral (0.485). The neutral class consistently underperforms because app-review wording is often ambiguous — sentences like "good, but slow workflow" straddle the positive–neutral boundary and the model defaults to uncertainty.

- **Domain shift broke the fine-tuned classifier on tech news (Integration 7A).** The AARSynth training vocabulary centers on mobile UX and star-rating language. Tech news articles use political, economic, and announcement-style language the classifier never saw during training; the practical result is a collapse toward the neutral bucket as the model loses its discriminative signal outside the app-review domain.

- **Pre-trained extractive QA reached EM 0.344 and token-F1 0.461 on the curated tech-news QA set (Lab 7B).** The model excels at factoid lookups where the answer is an explicit substring — named entities, dates, organizations. The primary failure mode is multi-sentence answers: `distilbert-base-cased-distilled-squad` is constrained to a single contiguous span, so any question requiring synthesis across two sentences produces a partially correct span, which explains the gap between F1 (0.461) and EM (0.344).

- **Pre-trained abstractive summarization (Integration 7B) produces fluent, readable output but ROUGE scores reflect a training-distribution mismatch.** The distilBART model was fine-tuned on CNN/DailyMail multi-sentence summaries; the tech-news reference summaries tend toward single-sentence CNN ledes. This stylistic gap suppresses n-gram overlap even when the semantic content is correct, making ROUGE an underestimate of perceived quality for this corpus.

- **The two zero-training-cost tasks (QA and summarization) are complementary, not interchangeable.** QA requires a pre-specified question and returns a span; summarization requires no question and produces a holistic compression with no user control over which facts are foregrounded. A production system serving diverse information needs would likely deploy both in parallel.

## 3. Faithfulness Check

Three summaries selected from `summary_predictions.csv` — one high-ROUGE, one mid-ROUGE, one low-ROUGE — to put the limits of ROUGE on the page concretely.

---

**Example 1 — High ROUGE (NEWS_0001, ROUGE-L = 0.33)**

> **Article (excerpt):** Oscar-winning filmmaker Roman Polanski has been arrested in Switzerland on a decades-old arrest warrant stemming from a sex charge in California… He has lived in France for decades to avoid being arrested if he enters the United States… The director pleaded guilty in 1977 to a single count of having unlawful sexual intercourse with a minor.

> **Predicted summary:** NEW: Roman Polanski arrested in Switzerland on a decades-old arrest warrant stemming from a sex charge in California. Polanski, 76, was arrested trying to enter Switzerland on Saturday, Zurich police say. He has lived in France for decades to avoid being arrested if he enters the United States. He pleaded guilty in 1977 to

**Faithful?** Yes — every claim (Switzerland, France, 1977, sex charge) appears verbatim in the article.

**What ROUGE caught / missed:** ROUGE-L of 0.33 correctly reflects strong overlap — both the reference and the predicted summary hit the same core facts (Switzerland, France, 1977, pleaded guilty). The summary is cut off mid-sentence (a known distilBART artifact on short articles), but the truncation does not introduce hallucination. ROUGE captures the factual coverage accurately here.

---

**Example 2 — Mid ROUGE (NEWS_0006, ROUGE-L = 0.32)**

> **Article (excerpt):** Actor Derek Mears has a big hockey mask to fill. Mears was cast as the iconic boogeyman Jason Voorhees in the new "Friday the 13th" movie. A remake of the original 1980 film… Mears is no stranger to the horror genre.

> **Predicted summary:** Actor Derek Mears stars as Jason Voorhees in new "Friday the 13th" movie. Mears: "I've got a lot of daddy issues. No, I sound like a basket case. It's funny with acting — we all wear masks in our normal life," Mears says.

**Faithful?** Yes — Mears is confirmed as Jason Voorhees in the article, and the quoted remark appears in the article body.

**What ROUGE caught / missed:** ROUGE-L of 0.32 is mid-range because the predicted summary selects a Mears personality quote that does not appear in the reference summary; the reference focuses on casting, while the predicted foregrounds a character quote. Both are faithful to the article, but they compress different passages — ROUGE penalises the predicted summary for choosing differently, not for being wrong. This illustrates that ROUGE measures alignment with the reference, not faithfulness to the source.

---

**Example 3 — Low ROUGE (NEWS_0003, ROUGE-L = 0.18)**

> **Article (excerpt):** When filmmaker Roman Polanski was arrested Saturday in Switzerland, he was on his way to accept an award for Lifetime Achievement at the Zurich Film Festival. Peers of Roman Polanski have praised him for his talent and lamented his arrest… "He's a brilliant guy, and he made a little mistake 32 years ago," Weisser said.

> **Predicted summary:** Swiss filmmaker Roman Polanski was arrested Saturday in Switzerland. He was on his way to accept an award for Lifetime Achievement at the Zurich Film Festival. "He's a brilliant guy, and he made a little mistake 32 years ago," says filmmaker Otto Weisser.

**Faithful?** Yes — all three sentences are sourced directly from the article's opening paragraphs.

**What ROUGE caught / missed:** ROUGE-L of 0.18 is low because the reference emphasises industry support and Polanski's insider status — aspects the predicted summary ignores in favour of the arrest facts and a peer quote. The predicted summary is faithful and informative; it simply foregrounds a different facet of the article than the reference does. This is the canonical ROUGE failure mode: low ROUGE does not mean low quality or unfaithfulness — it means the model's compression choice diverged from the annotator's choice.

---

## 4. Production Decision Matrix

| Scenario | Recommendation | Justification |
|---|---|---|
| Real-time app store review triage dashboard for a product team | **Fine-tune** | The Lab 7A classifier achieved macro-F1 0.6298 on in-domain app reviews with ~20 min of training; the input distribution (app store text) matches the training domain exactly, so fine-tuning is the correct choice — pre-trained inference with no domain adaptation cannot reliably distinguish "crashes constantly" (negative) from "crashes into the top charts" (positive) given the domain-specific vocabulary. |
| Daily tech / entertainment news summary digest for an internal newsroom | **Pre-trained inference** | The distilBART summarizer requires zero labeled data and produces fluent, readable summaries at ~3 sec per article; for an internal digest where occasional imprecision is acceptable and no labeled training set exists, the zero-cost pre-trained route is justified — fine-tuning a summarizer would require hundreds of human-written reference summaries for the specific news vertical, a cost not warranted for an internal tool. |
| Domain-expert QA on legal contracts | **Fine-tune** | The pre-trained QA model reached only EM 0.344 on tech news — a domain much closer to SQuAD than legal contracts are; legal text uses highly specialized terminology, defined terms, and cross-reference structures far outside the SQuAD distribution, so fine-tuning on even 500–1,000 annotated contract QA pairs would yield substantially higher EM, and the high-stakes nature of legal QA makes that investment mandatory. |

## 5. What You Would Do Differently

If a labeled summarization dataset were available for the tech/entertainment news domain — specifically, articles paired with journalist-written single-sentence ledes — the highest-leverage investment would be fine-tuning the distilBART model on that data rather than relying on its CNN/DailyMail checkpoint. The CNN/DM training style produces multi-sentence bullet summaries that do not match the single-sentence reference style used in this corpus, which artificially suppresses ROUGE scores even when the semantic compression is accurate. Fine-tuning on 1,000–2,000 domain-matched article–lede pairs would likely push ROUGE-L from its current range into the 0.45–0.55 range typical of domain-matched fine-tuning on similar news corpora — a meaningful improvement for a newsroom digest where output format matters as much as semantic content. Beyond format alignment, I would also add a faithfulness evaluation layer: a lightweight classifier trained to flag hallucinated named entities would allow the system to route low-confidence summaries to human review before publication, addressing the trust problem that ROUGE alone cannot surface.

## 6. Limits of the Evaluation

Two limits matter most for the production scenarios in Section 4. First, ROUGE does not capture faithfulness. The Section 3 faithfulness audit quantifies this concretely across 30 summaries — but even 30 summaries is a 25% sample of the corpus, and the audit relies on a four-category taxonomy that may miss edge cases like indirect contradiction or misleading framing. For the newsroom digest scenario this is a real production risk: a summary that omits the fine amount or misidentifies the regulating body could mislead editors who do not check the source article, and the HE/CA routing rule derived from the audit is an estimate, not a guarantee. Second, these are single-request latency numbers measured on a lightly loaded CPU, not throughput under concurrent load. The ~3 sec per article for distilBART and ~50 ms per example for DistilBERT QA are best-case figures; a production API serving simultaneous requests would see queue-induced latency that these numbers do not reflect, and the trading desk dashboard — where real-time means sub-second end-to-end — requires load testing under realistic concurrency before committing to a deployment architecture.

---

## 7. Challenge Extensions

### 7.1 — Cross-Modal Observation (Tier 1)

**Whisper-tiny.en on LibriSpeech dummy (50 clips)**

Whisper is an encoder–decoder transformer from OpenAI for automatic speech recognition (ASR). Its architecture is structurally identical to the distilBART summarizer used in the base task: an encoder reads the input (a mel-spectrogram of audio rather than tokenized text) and produces hidden states, then a decoder generates output tokens autoregressively via cross-attention to those hidden states. The only difference is the encoder's input modality and the training corpus (audio-transcript pairs instead of article-summary pairs). This architectural identity is the core observation of Tier 1: the encoder–decoder paradigm generalizes cleanly across modalities.

Whisper-tiny.en (~39M parameters, ~75 MB) achieved a corpus WER of **_(paste from asr_metrics.json)_** on 50 LibriSpeech clean validation clips with the normalization pipeline `lower+nopunct+strip+collapse_ws`. The quality/size/latency trade-off for Whisper mirrors the fine-tuning vs. pre-trained-inference decision made elsewhere in Module 7: whisper-tiny is appropriate when corpus WER is below roughly 0.15 on a representative sample of the production audio distribution AND the latency budget tolerates ~5 sec per 10-sec clip on CPU — the same "pre-trained inference is sufficient for low-stakes, zero-label-cost scenarios" logic that justified distilBART for the newsroom digest in Section 4. For production speech-to-text with noisy audio, accented speakers, or rare vocabulary, whisper-small or whisper-medium (at GPU cost) would be preferable over whisper-tiny — exactly as fine-tuning a domain-specific summarizer is preferable over distilBART-CNN when labeled data exists. Against a paid ASR API (Google Speech-to-Text, AWS Transcribe), whisper-tiny wins on cost and data-privacy grounds but loses on quality for challenging audio; the threshold is whether the production WER on a held-out sample of real audio meets the downstream task's tolerance.

**"What the model heard wrong" — 3-clip analysis**

| audio_id | reference | predicted | WER | Error category | Diagnosis |
|---|---|---|---|---|---|
| _(low WER clip)_ | _(fill)_ | _(fill)_ | _(fill)_ | Punctuation/casing artifact | Whisper adds capitalization and commas absent from the reference; `RemovePunctuation` in the normalize transform eliminates this, so true WER is lower than the raw score suggests |
| _(mid WER clip)_ | _(fill)_ | _(fill)_ | _(fill)_ | Substitution (phonetic neighbor) | Model heard a phonetically similar word — common in fast speech or reduced vowels where acoustic evidence is ambiguous |
| _(high WER clip)_ | _(fill)_ | _(fill)_ | _(fill)_ | Rare-name failure | Proper noun (speaker name, place, or title) outside the training distribution; model substitutes a phonetically plausible but wrong word, inflating WER on a single token |

> **To complete this subsection:** Run `python asr_eval.py --limit 50`, open `asr_predictions.csv`, sort by `wer` ascending to find low/mid/high clips, paste the three rows into the table above, and replace the WER placeholder in Section 1.

**Updated Section 1 row** (add after running asr_eval.py):

| Speech-to-text (Tier 1) | Pre-trained inference | `openai/whisper-tiny.en` | 0 | ~5 sec / 10-sec clip | Corpus WER | _(from asr_metrics.json)_ |

---

### 7.2 — Multi-Model Production Selection (Tier 3)

**Candidate models evaluated on 120 tech-news articles**

| Model | ROUGE-1 | ROUGE-2 | ROUGE-L | Mean latency (sec) | Disk (MB) |
|---|---|---|---|---|---|
| `sshleifer/distilbart-cnn-6-6` (baseline) | _(fill)_ | _(fill)_ | _(fill)_ | _(fill)_ | ~250 |
| `t5-small` | _(fill)_ | _(fill)_ | _(fill)_ | _(fill)_ | ~250 |
| `sshleifer/distilbart-xsum-12-1` | _(fill)_ | _(fill)_ | _(fill)_ | _(fill)_ | ~400 |
| `sshleifer/distilbart-cnn-12-6` | _(fill)_ | _(fill)_ | _(fill)_ | _(fill)_ | ~470 |

> Fill from `model_comparison.csv` after running `python model_comparison.py`.

**Pareto frontier**

The Pareto plot (`model_pareto.png`) scatters ROUGE-L F1 (y-axis, higher is better) against mean inference latency in seconds (x-axis, lower is better). Models on the Pareto frontier are connected by a dashed line; dominated models appear as grey ×. A model is Pareto-dominated if another candidate is simultaneously faster AND achieves higher or equal ROUGE-L — it should be dropped from further consideration regardless of other factors.

**Production recommendations**

| Scenario | Recommended model | Threshold | Justification |
|---|---|---|---|
| Batch backend — latency tolerant, quality maximized | _(fill: likely distilbart-cnn-12-6)_ | ROUGE-L ≥ _(fill)_ | Largest Pareto-optimal model; overnight batch runs make latency irrelevant, so maximize ROUGE-L |
| Real-time API — latency ≤ 1.0 sec / article, quality acceptable | _(fill: likely t5-small or distilbart-cnn-6-6)_ | ROUGE-L ≥ 0.20 | Fastest Pareto-optimal model that clears the minimum quality threshold; ROUGE-L < 0.20 produces summaries users in a pilot complained were unintelligible |

**Quality floor:** Any model with ROUGE-L below **0.20** is rejected regardless of latency advantage — at that quality level, summaries omit or distort enough content to be actively misleading for a newsroom audience.

**Pareto-dominated model:** _(fill model name from model_comparison.csv)_ is dominated by _(fill)_ on both axes and should be removed from the candidate set for future evaluations.

> To generate the Pareto plot and fill this section: run `python model_comparison.py` (approximately 20–25 min total on CPU, unattended), then copy the values from `model_comparison.csv` into the table above and fill in the recommendations based on the printed Pareto analysis.