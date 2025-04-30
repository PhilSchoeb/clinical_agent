import os
import json
import random

"""
This script randomizes the 'Correct disease' field in synthetic patient JSON files
by replacing it with an alternate disease name (from an expert-validated mapping).
It also updates the 'altName' field with all valid variants and replaces matching
entries in the 'Mixed diseases' field accordingly.

Supported JSON formats:
- A single dictionary with a 'patients' list
- A list of patient dictionaries
- A list of dictionaries each containing a 'patients' list

The modified JSON files are written to a specified output folder.
"""


def load_alt_map(alt_json_path: str) -> dict[str, list[str]]:
    with open(alt_json_path, 'r', encoding='utf-8') as f:
        entries = json.load(f)

    alt_map: dict[str, list[str]] = {}
    for entry in entries:
        title = entry.get('title', '').strip()
        raw = entry.get('altTitle') or ''
        alts = [
            a.strip() for a in raw.split(',')
            if a.strip() and a.strip().lower() != 'none'
        ]
        alt_map[title] = alts
    return alt_map


def randomize_patients(patients: list[dict], alt_map: dict[str, list[str]]):
    for p in patients:
        orig = p.get('Correct disease', '').strip()
        if not orig or orig not in alt_map:
            continue

        choices = [orig] + alt_map[orig]
        p['altName'] = choices

        new_name = random.choice(choices)
        p['Correct disease'] = new_name

        p['Mixed diseases'] = [
            new_name if d == orig else d
            for d in p.get('Mixed diseases', [])
        ]


def process_file(
        input_path: str,
        output_path: str,
        alt_map: dict[str, list[str]]
):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, dict) and 'patients' in data:
        randomize_patients(data['patients'], alt_map)

    elif isinstance(data, list) and data and isinstance(data[0], dict) and 'patients' in data[0]:
        for group in data:
            if isinstance(group, dict) and 'patients' in group:
                randomize_patients(group['patients'], alt_map)

    elif isinstance(data, list) and data and isinstance(data[0], dict):
        randomize_patients(data, alt_map)

    else:
        print(f"Skipping {os.path.basename(input_path)}: format not recognized")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f" Wrote randomized file: {os.path.basename(output_path)}")


if __name__ == '__main__':
    summary_file = '../data/resources/infection_parasits_diseases/diseases_alt_name.json'
    alt_map = load_alt_map(summary_file)

    in_dir = '../data/infection_diseases/patients'
    out_dir = '../data/infection_diseases/patients_randomized'

    for fname in sorted(os.listdir(in_dir)):
        if not fname.endswith('.json'):
            continue
        inp = os.path.join(in_dir, fname)
        out = os.path.join(out_dir, fname)
        process_file(inp, out, alt_map)

    print("All done.")
