import os
import json

"""
This script extracts all unique disease titles from a folder of JSON files 
(previously parsed from XML disease descriptions) and saves them into a 
plain text file, one title per line.

Steps:
1. Iterates over JSON files and collects all 'title' values under 'parsed_data' → 'titles'.
2. Deduplicates and sorts the titles.
3. Writes the result to a specified .txt output file.

Useful for generating a clean reference list of disease names.
"""


def extract_unique_disease_titles(folder_path):
    unique_titles = set()

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    titles = data.get("parsed_data", {}).get("titles", [])
                    for entry in titles:
                        title = entry.get("title")
                        if title:
                            unique_titles.add(title.strip())
            except json.JSONDecodeError:
                print(f"Warning: Failed to decode JSON in {filename}")

    return unique_titles


def save_titles_to_txt(titles, output_file):
    with open(output_file, "w", encoding='utf-8') as f:
        for title in sorted(titles):
            f.write(title + "\n")
    print(f"Saved {len(titles)} unique disease titles to {output_file}")


def main():
    input_folder = "../data/infection_diseases/json"
    output_file = "../data/resources/infection_parasits_diseases/unique_infection_diseases.txt"

    unique_titles = extract_unique_disease_titles(input_folder)
    save_titles_to_txt(unique_titles, output_file)


if __name__ == "__main__":
    main()
