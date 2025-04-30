import os
import glob
import json

"""
This script removes all synthetic patient entries labeled with the disease 
"Aneurysms" from JSON files in a specified folder. Each JSON file contains 
groups of patients, and only those not labeled with "Aneurysms" as their 
'Correct disease' are retained. Modified files are saved in place, and a 
summary of deleted entries is printed.
"""


def remove_aneurysms_patients(folder_path: str):
    total_deleted = 0

    # find all .json files
    for filepath in glob.glob(os.path.join(folder_path, "*.json")):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        file_deleted = 0
        for entry in data:
            patients = entry.get("patients", [])
            original_count = len(patients)

            # if Correct disease is not "Aneurysms"
            filtered_patients = [
                p for p in patients
                if p.get("Correct disease") != "Aneurysms"
            ]
            deleted = original_count - len(filtered_patients)
            if deleted > 0:
                entry["patients"] = filtered_patients
                file_deleted += deleted

        if file_deleted > 0:
            total_deleted += file_deleted
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Removed {file_deleted} patients from {os.path.basename(filepath)}")

    print(f"Total patients removed across all files: {total_deleted}")


if __name__ == "__main__":
    folder = "../AgentHospital_Data/agent_patients/patient_heart_modified"
    remove_aneurysms_patients(folder)
