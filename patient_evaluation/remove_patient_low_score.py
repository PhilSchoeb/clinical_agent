import os
import json
import csv
import glob

"""
This script filters out synthetic patients marked as 'Unpassable' in an evaluation CSV file.
It performs the following steps:

1. Loads patient numbers labeled 'Unpassable' from a CSV file.
2. Iterates through JSON files in a folder and removes matching patients based on their 'patient_number'.
3. Optionally saves the cleaned files to a separate output folder, or overwrites the original files.
4. Logs which patients were removed from each file and prints the total count.

Useful for cleaning datasets after cosine/BERTScore-based evaluations.
"""

def filter_unpassable_patients(json_folder: str, csv_path: str, output_folder: str = None):
    # --- 1) load all unpassable patient numbers
    unpassable_nums = set()
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['result'].strip().lower() == 'unpassable':
                unpassable_nums.add(row['patient_number'].strip())

    total_removed = 0

    target_folder = output_folder or json_folder
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)

    # --- 2) process each JSON file
    for json_file in glob.glob(os.path.join(json_folder, '*.json')):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        removed_nums = []
        for entry in data:
            original = entry.get('patients', [])
            # collect patient_numbers to remove
            for p in original:
                num = p.get('patient_number', '').strip()
                if num in unpassable_nums:
                    removed_nums.append(num)

            # filter out the unpassable patients
            entry['patients'] = [
                p for p in original
                if p.get('patient_number', '').strip() not in unpassable_nums
            ]

        if removed_nums:
            total_removed += len(removed_nums)
            print(f"{os.path.basename(json_file)}: removed {len(removed_nums)} patient(s) -> {', '.join(removed_nums)}")

        out_path = os.path.join(target_folder, os.path.basename(json_file))
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Total patients removed across all files: {total_removed}")


if __name__ == '__main__':
    json_input_folder  = '../llama3_8B_cleaned_1/patient_infection_modifed'
    csv_file           = 'cosine_mean_results_infection_disease.csv'
    json_output_folder = '../llama3_8B_cleaned_1/cosine_patient_infection_modifed'

    filter_unpassable_patients(json_input_folder, csv_file, json_output_folder)
