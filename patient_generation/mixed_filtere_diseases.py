import os
import json

"""
This script extracts unique disease names from a log file generated during synthetic patient creation. 
It searches for lines matching the pattern 'Generating <N> profiles for <Disease Name>', 
deduplicates the disease names, and writes the result to an output file.

Steps:
1. Verifies the input file exists.
2. Parses the file using regex to extract disease names.
3. Skips duplicates and logs them.
4. Saves the list of unique diseases to the specified output path.
"""


def extract_titles(input_dir: str, output_file: str) -> None:
    all_entries = []
    for fname in sorted(os.listdir(input_dir)):
        if not fname.endswith('.json'):
            continue

        path = os.path.join(input_dir, fname)
        print(f"Reading {path}…")
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for entry in data.get('parsed_data', {}).get('titles', []):
            title = (entry.get('title') or "").strip()
            alt = (entry.get('altTitle') or "").strip()
            if not alt:
                alt = "None"
            all_entries.append({'title': title, 'altTitle': alt})

    print(f"\n[Extract] Collected {len(all_entries)} entries total.\n")
    with open(output_file, 'w', encoding='utf-8') as out:
        json.dump(all_entries, out, ensure_ascii=False, indent=2)
    print(f"[Extract] Wrote summary to: {output_file}\n")


def filter_and_dedupe_summary(
        summary_json: str,
        unique_txt: str
):
    # 1) load unique names
    with open(unique_txt, 'r', encoding='utf-8') as f:
        unique_set = {line.strip().lower() for line in f if line.strip()}
    print(f"[Filter] Loaded {len(unique_set)} unique names from TXT.\n")

    # 2) load summary
    with open(summary_json, 'r', encoding='utf-8') as f:
        entries = json.load(f)
    if not isinstance(entries, list):
        raise RuntimeError("Summary JSON must be a top-level list.")

    print(f"[Filter] Summary has {len(entries)} entries before filtering.\n")

    # 3) filter + 4) dedupe
    kept = []
    seen = set()
    dropped = 0

    for e in entries:
        title_low = e['title'].lower()
        alt_lows = [a.strip().lower() for a in e['altTitle'].split(',') if a.strip()]

        match = (title_low in unique_set) or any(a in unique_set for a in alt_lows)
        if not match:
            dropped += 1
            continue

        # dedupe by title
        if title_low in seen:
            continue
        seen.add(title_low)
        kept.append(e)

    print(f"[Filter] Dropped {dropped} non-matches; kept {len(kept)} unique matches.\n")

    # 5) write back
    with open(summary_json, 'w', encoding='utf-8') as f:
        json.dump(kept, f, ensure_ascii=False, indent=2)
    print(f"[Filter] Overwritten {summary_json} with {len(kept)} entries.\n")


if __name__ == '__main__':
    input_dir = '../data/infection_diseases/json'
    summary_file = '../data/resources/infection_parasits_diseases/diseases_alt_name.json'
    extract_titles(input_dir, summary_file)

    unique_txt = '../data/resources/infection_parasits_diseases/disease_list_filtered.txt'
    filter_and_dedupe_summary(summary_file, unique_txt)
