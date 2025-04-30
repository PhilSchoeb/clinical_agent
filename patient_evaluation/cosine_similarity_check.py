# https://sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html
import argparse
import os
import glob
import json
import csv
from sentence_transformers import SentenceTransformer, util
from nltk.tokenize import sent_tokenize

"""
This script evaluates the semantic similarity between synthetic patient symptoms 
and expert-written disease summaries using mean top-K cosine similarity. 
It uses a Sentence-BERT (SBERT) model, such as Bio_ClinicalBERT, to embed texts 
and calculate similarity scores. The evaluation helps determine whether the 
generated patient profiles are meaningfully aligned with their corresponding 
disease summaries. Results are saved to a CSV file.
"""


def resolve_path(path: str, base_dir: str) -> str:
    return path if os.path.isabs(path) else os.path.abspath(os.path.join(base_dir, path))


def load_summary_data(summary_file_path: str) -> dict:
    with open(summary_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    mapping = {}
    for item in data.get("parsed_data", {}).get("titles", []):
        title = item.get("title")
        summary = item.get("FullSummary", "")
        if title:
            mapping[title] = summary
    return mapping


def load_patient_data(patient_file_path: str):
    with open(patient_file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_cosine(summary_dir: str,
                    patient_dir: str,
                    output_csv: str,
                    threshold: float,
                    top_k: int,
                    model_name: str):
    # Load SBERT model
    model = SentenceTransformer(model_name)

    total_passable = 0
    total_unpassable = 0

    out_dir = os.path.dirname(output_csv) or '.'
    os.makedirs(out_dir, exist_ok=True)

    with open(output_csv, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["patient_id", "mean_cosine", "result"])

        # Iterate summary files
        for summary_file in glob.glob(os.path.join(summary_dir, "*.json")):
            disease_key = os.path.splitext(os.path.basename(summary_file))[0]
            patient_file = os.path.join(patient_dir, f"patients_{disease_key}.json")
            if not os.path.exists(patient_file):
                print(f"[WARNING] No patient file for {disease_key}, skipping.")
                continue

            print(f"\nProcessing disease: {disease_key}")
            summary_map = load_summary_data(summary_file)
            patient_groups = load_patient_data(patient_file)

            # Pre-tokenize and embed summary
            for group in patient_groups:
                disease_name = group.get("disease")
                full_summary = summary_map.get(disease_name, "")
                if not full_summary:
                    print(f"  [SKIP] No summary for {disease_name}")
                    continue

                sentences = sent_tokenize(full_summary)
                sent_embeddings = model.encode(sentences, convert_to_tensor=True)

                for patient in group.get("patients", []):
                    pid = patient.get("patient_number")
                    symptoms = patient.get("Symptoms", "").strip()
                    if not symptoms:
                        continue

                    patient_emb = model.encode(symptoms, convert_to_tensor=True)
                    cos_scores = util.cos_sim(patient_emb, sent_embeddings)[0]
                    # Select top-K and compute mean
                    top_scores = sorted(cos_scores, reverse=True)[:top_k]
                    mean_cosine = float(sum(top_scores) / top_k)

                    result = "Passable" if mean_cosine >= threshold else "Unpassable"
                    writer.writerow([pid, f"{mean_cosine:.4f}", result])

                    if result == "Passable":
                        total_passable += 1
                    else:
                        total_unpassable += 1

                    print(f"  Patient {pid}: mean_cosine={mean_cosine:.4f} -> {result}")

    # Final summary
    print("\n=== Final Evaluation ===")
    print(f"Total Passable:   {total_passable}")
    print(f"Total Unpassable: {total_unpassable}")
    print(f"Results written to '{output_csv}'")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate synthetic patients using mean top-K cosine similarity"
    )
    parser.add_argument(
        'summary_dir',
        help="Directory of disease summary JSON files"
    )
    parser.add_argument(
        'patient_dir',
        help="Directory of patient JSON files: patients_<disease>.json"
    )
    parser.add_argument(
        'output_csv',
        help="Path to output CSV file"
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.75,
        help="Minimum mean cosine to mark Passable (default: 0.75)"
    )
    parser.add_argument(
        '--top_k',
        type=int,
        default=3,
        help="Number of top sentences to average (default: 3)"
    )
    parser.add_argument(
        '--model_name',
        default='emilyalsentzer/Bio_ClinicalBERT',
        help="SBERT model name (default: emilyalsentzer/Bio_ClinicalBERT)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    base_dir = os.path.dirname(os.path.abspath(__file__))

    summary_dir = resolve_path(args.summary_dir, base_dir)
    patient_dir = resolve_path(args.patient_dir, base_dir)
    output_csv = resolve_path(args.output_csv, base_dir)

    evaluate_cosine(
        summary_dir,
        patient_dir,
        output_csv,
        args.threshold,
        args.top_k,
        args.model_name
    )


if __name__ == '__main__':
    main()
