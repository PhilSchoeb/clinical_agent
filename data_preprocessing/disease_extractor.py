from utils.file_handler import read_pdf
from .data_extractor import DataExtractor
import re
"""
This module provides a `DiseaseExtractor` class specialized in parsing disease-related PDF files,
particularly for structured extraction of headings and sublines from cardiology or departmental documents.

Key functionalities:
- Identifies headings based on patterns like '(digits–digits)'.
- Extracts sublines based on digit-starting lines.
- Cleans the results by removing numerical codes and filtering out generic terms like 'other' or 'unspecified'.

Used for converting raw PDF text into structured, cleaned dictionaries for downstream processing.
"""


def clean_results(data):
    """
    1) Remove all numeric codes and (digits–digits) patterns from headings & sublines.
    2) Remove sublines they are exactly "other", "unspecified", or "other and unspecified".
    """
    skip_exact = {"other", "unspecified", "other and unspecified", "elsewhere"}
    cleaned_data = {}

    for heading, sub_lines in data.items():
        cleaned_heading = re.sub(r'\(\d+.*?\d+\)', '', heading)  # remove ranges
        cleaned_heading = cleaned_heading.strip().lower()

        # Remove number in subline
        cleaned_sublist = []
        for line in sub_lines:
            line_clean = re.sub(r'\d+(\.\d+)?', '', line)
            line_clean = line_clean.strip().lower()

            # Exactly matching the skip list
            if line_clean not in skip_exact and line_clean:
                cleaned_sublist.append(line_clean)

        # If the heading isn't empty after cleaning=> skip
        if cleaned_heading:
            cleaned_data[cleaned_heading] = cleaned_sublist

    return cleaned_data


def parse_heart_disease(raw_pdf_data):
    results = {}
    current_heading = None

    i = 0
    while i < len(raw_pdf_data):
        line = raw_pdf_data[i].strip()

        # Skip empty lines
        if not line:
            i += 1
            continue

        # If the line ALREADY contains (digits–digits), treat as heading
        if re.search(r'\(\d+\s*[\-–—]\s*\d+(\.\d+)?\)', line):
            current_heading = line
            results[current_heading] = []
            i += 1

        # If line starts with digits => subline
        elif re.match(r'^\d', line):
            if current_heading:
                results[current_heading].append(line)
            i += 1

        # Else the line has NO digits => check next line for special case
        else:
            if i < len(raw_pdf_data) - 1:
                next_line = raw_pdf_data[i + 1].strip()

                # If the next line is EXACTLY (digits–digits), merge them
                if re.match(r'^\(\d+\s*[\-–—]\s*\d+(\.\d+)?\)$', next_line):
                    heading_line = line + " " + next_line
                    current_heading = heading_line
                    results[current_heading] = []
                    i += 2  # Skip the next line
                else:
                    i += 1  # Not a heading => skip this line
            else:
                i += 1  # No next line => skip

    return clean_results(results)


class DiseaseExtractor(DataExtractor):
    """
    Specialized extractor for departement(pe. cardiologie) disease PDF files.
    """

    def extract_information(self, file_path):
        # TODO: autorun for more than one disease
        data = read_pdf(file_path)  # only one disease
        return parse_heart_disease(data)
