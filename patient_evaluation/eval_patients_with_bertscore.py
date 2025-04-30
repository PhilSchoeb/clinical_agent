import argparse
import json
import csv
import os
import glob
from bert_score import score

"""
This script evaluates the semantic similarity between synthetic patient symptoms 
and expert-authored disease summaries using BERTScore. Each patient profile is 
compared to its corresponding full disease summary, and the F1-score is computed 
using a specified transformer model (e.g., Clinical-Longformer). Results are 
saved in a CSV file with each patient's ID, BERTScore F1, and a Passable/Unpassable label 
based on a predefined threshold.
"""


def resolve_path(path: str, base_dir: str) -> str:
    return path if os.path.isabs(path) else os.path.abspath(os.path.join(base_dir, path))


def load_summary_data(summary_file_path):
    with open(summary_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    summary_mapping = {}
    for item in data.get("parsed_data", {}).get("titles", []):
        disease = item.get("title")
        full_summary = item.get("FullSummary", "")
        if disease:
            summary_mapping[disease] = full_summary
    return summary_mapping


def load_patient_data(patient_file_path):
    """
    Load the patients JSON file.
    """
    with open(patient_file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_bertscore(summary_dir, patient_dir, output_csv, threshold,
                       model_type, lang, num_layers):
    total_passable = 0
    total_unpassable = 0

    os.makedirs(os.path.dirname(output_csv) or '.', exist_ok=True)
    with open(output_csv, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["patient_id", "bert_score", "result"])

        summary_files = glob.glob(os.path.join(summary_dir, "*.json"))
        for summary_file in summary_files:
            base_name = os.path.splitext(os.path.basename(summary_file))[0]
            patient_file = os.path.join(patient_dir, f"patients_{base_name}.json")
            if not os.path.exists(patient_file):
                print(f"Patient file for '{base_name}' not found. Skipping.")
                continue

            print(f"\nProcessing disease '{base_name}'...")
            summary_mapping = load_summary_data(summary_file)
            patient_data = load_patient_data(patient_file)

            for group in patient_data:
                disease_name = group.get("disease")
                full_summary = summary_mapping.get(disease_name, "")
                if not full_summary:
                    print(f"  No summary for '{disease_name}', skip group.")
                    continue

                for patient in group.get("patients", []):
                    symptoms = patient.get("Symptoms", "").strip()
                    if not symptoms:
                        continue

                    P, R, F1 = score(
                        [symptoms],
                        [full_summary],
                        model_type=model_type,
                        lang=lang,
                        num_layers=num_layers
                    )
                    f1 = F1.item()
                    result = "Passable" if f1 > threshold else "Unpassable"

                    writer.writerow([patient.get("patient_number"), f"{f1:.4f}", result])
                    if result == "Passable":
                        total_passable += 1
                    else:
                        total_unpassable += 1

                    print(f"  Patient {patient.get('patient_number')}: F1={f1:.4f} -> {result}")

    print("\nFinal Evaluation:")
    print(f"  Total Passable:   {total_passable}")
    print(f"  Total Unpassable: {total_unpassable}")
    print(f"CSV file '{output_csv}' created.")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate synthetic patients against expert summaries using BERTScore"
    )
    parser.add_argument(
        "summary_dir",
        help="Directory containing disease summary JSON files (*.json)"
    )
    parser.add_argument(
        "patient_dir",
        help="Directory containing patient JSON files named patients_<disease>.json"
    )
    parser.add_argument(
        "output_csv",
        help="Path to write the evaluation results CSV"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.75,
        help="F1-score threshold to mark a patient as Passable (default: 0.75)"
    )
    parser.add_argument(
        "--model_type",
        default="yikuan8/Clinical-Longformer",
        help="Model name for BERTScore"
    )
    parser.add_argument(
        "--lang",
        default="en",
        help="Language code for BERTScore"
    )
    parser.add_argument(
        "--num_layers",
        type=int,
        default=12,
        help="Number of layers to use in the scorer"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    base_dir = os.path.dirname(os.path.abspath(__file__))

    summary_dir = resolve_path(args.summary_dir, base_dir)
    patient_dir = resolve_path(args.patient_dir, base_dir)
    output_csv = resolve_path(args.output_csv, base_dir)

    evaluate_bertscore(
        summary_dir,
        patient_dir,
        output_csv,
        args.threshold,
        args.model_type,
        args.lang,
        args.num_layers
    )


if __name__ == "__main__":
    main()
