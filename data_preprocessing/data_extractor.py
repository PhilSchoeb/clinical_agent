import os
from utils.file_handler import output_json, read_pdf

"""
This module defines a DataExtractor class for extracting text content from PDF files
and saving the extracted data to JSON format. It uses utility functions from 
`utils.file_handler` for reading and writing files.
"""


class DataExtractor:
    def __init__(self, output_dir="data/resources"):
        self.output_dir = output_dir

    def extract_information(self, file_path):
        if file_path.endswith('.pdf'):
            return read_pdf(file_path)
        else:
            return None

    def process_file(self, file_path):
        extracted_data = self.extract_information(file_path)
        if extracted_data:
            filename_without_ext = os.path.splitext(os.path.basename(file_path))[0]
            output_file = os.path.join(self.output_dir, filename_without_ext)
            output_json(output_file, extracted_data)
            print(f"Saved extracted data to {output_file}.json")
        else:
            print(f"No data extracted from {file_path}")
