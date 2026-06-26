# asr_eval.py
import argparse
import csv
import json

import jiwer
from datasets import load_dataset
from transformers import pipeline

MODEL = "openai/whisper-tiny.en"

NORMALIZE = jiwer.Compose([
    jiwer.ToLowerCase(),
    jiwer.RemovePunctuation(),
    jiwer.RemoveMultipleSpaces(),
    jiwer.Strip(),
    jiwer.ReduceToListOfListOfWords(),
])


def compute_wer(reference, hypothesis):
    """Compute WER with explicit normalization."""
    out = jiwer.process_words(
        reference,
        hypothesis,
        reference_transform=NORMALIZE,
        hypothesis_transform=NORMALIZE,
    )
    return out.wer


def main(limit: int) -> None:
    print(f"Loading LibriSpeech dummy dataset (limit={limit})...")
    ds = load_dataset(
        "hf-internal-testing/librispeech_asr_dummy",
        "clean",
        split="validation",
    ).select(range(limit))

    print(f"Loading Whisper model: {MODEL}")
    asr = pipeline("automatic-speech-recognition", model=MODEL)

    rows = []
    references = []
    predictions = []

    for i, row in enumerate(ds):
        print(f"  Clip {i+1}/{limit}...", end="\r")
        out = asr(row["audio"]["array"])
        predicted = out["text"]
        reference = row["text"]

        wer = compute_wer(reference, predicted)

        rows.append({
            "audio_id": f"clip_{i:03d}",
            "reference": reference,
            "predicted": predicted,
            "wer": round(wer, 4),
        })

        references.append(reference)
        predictions.append(predicted)

    print()

    # Corpus-level WER (weighted by reference length)
    corpus_out = jiwer.process_words(
        references,
        predictions,
        reference_transform=NORMALIZE,
        hypothesis_transform=NORMALIZE,
    )
    corpus_wer = corpus_out.wer

    # Write asr_predictions.csv
    with open("asr_predictions.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["audio_id", "reference", "predicted", "wer"])
        writer.writeheader()
        writer.writerows(rows)

    # Write asr_metrics.json
    metrics = {
        "wer": round(corpus_wer, 4),
        "n": limit,
        "model": MODEL,
        "normalization": "lower+nopunct+strip+collapse_ws",
    }
    with open("asr_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Corpus WER = {corpus_wer:.4f}")
    print(f"n = {limit}")
    print("Wrote: asr_predictions.csv, asr_metrics.json")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=50)
    args = p.parse_args()
    main(args.limit)