import os
import re
import sys

"""
This script extracts unique disease names from a log file generated during synthetic patient creation. 
It searches for lines matching the pattern 'Generating <N> profiles for <Disease Name>', 
reduplicates the disease names, and writes the result to an output file.

Steps:
1. Verifies the input file exists.
2. Parses the file using regex to extract disease names.
3. Skips duplicates and logs them.
4. Saves the list of unique diseases to the specified output path.
"""

def extract_unique_diseases(input_path: str, output_path: str) -> None:
    # 1) Check input file exists
    if not os.path.isfile(input_path):
        sys.exit(f"Input file not found: {input_path}")

    # 2) Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # 3) Regex to capture the disease name
    pattern = re.compile(r'Generating\s+\d+\s+profiles\s+for\s+(.+)$')

    seen = set()
    unique_diseases = []

    # 4) Read & dedupe
    with open(input_path, 'r', encoding='utf-8') as infile:
        for line in infile:
            m = pattern.search(line)
            if not m:
                continue
            name = m.group(1).strip()
            if name in seen:
                print(f"Duplicate found, skipping: {name}")
            else:
                seen.add(name)
                unique_diseases.append(name)

    # 5) Write output file
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for disease in unique_diseases:
            outfile.write(disease + '\n')

    print(f"Saved {len(unique_diseases)} unique disease names to {output_path}")


def main():
    input_path = '../data/resources/infection_parasits_diseases/disease_aborted_list.txt'
    output_path = '../data/resources/infection_parasits_diseases/disease_list_filtered.txt'

    extract_unique_diseases(input_path, output_path)


if __name__ == "__main__":
    main()
