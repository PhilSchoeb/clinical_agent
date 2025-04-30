import os
import json
from .data_extractor import DataExtractor
from utils.file_handler import read_xml
import xml.etree.ElementTree as ET
from pathlib import Path

"""
This module defines `DetailDiseaseExtractor`, a specialized class for extracting structured
information from disease-related XML files (e.g., heart or infectious diseases).

It supports:
- Parsing a single XML file into a structured dictionary.
- Batch-processing an entire directory of XML files and saving the parsed data as JSON.
It extends the `DataExtractor` class and utilizes utility functions for file handling.
"""


def parse_disease(xml_content, file_name=None):
    root = ET.fromstring(xml_content)
    term_text = root.findtext("term", default="").strip()

    cause_diagnosis = (
        file_name.replace(".xml", "").lower() if file_name else term_text.lower()
    )

    result = {"titles": []}

    if root.find("list") is not None:
        document_elems = root.findall("list/document")
    else:
        document_elems = root.findall("document")

    for doc_elem in document_elems:
        content_map = {}
        for content_elem in doc_elem.findall("content"):
            name_attr = content_elem.get("name", "").strip()
            text_value = (content_elem.text or "").strip()
            if name_attr:
                content_map.setdefault(name_attr, []).append(text_value)

        single_doc_obj = {key: ",".join(values) for key, values in content_map.items()}
        single_doc_obj["cause_diagnosis"] = cause_diagnosis  # inject cause
        result["titles"].append(single_doc_obj)

    return result


"""
   Specialized extractor for heart (or other) disease XML files.

   This extractor provides:
     - extract_information(file_path): Processes a single XML file and returns parsed data.
     - process_all_diseases(): Processes an entire folder structure where each subfolder represents
       a disease; all XML files in each subfolder are parsed and aggregated into one JSON file
       named after the subfolder.
   """


class DetailDiseaseExtractor(DataExtractor):

    def __init__(self, input_dir=None, output_dir=None):
        current_file = Path(__file__).resolve()  # Get the absolute path to this file
        project_root = current_file.parent.parent  # Get the project root
        self.input_dir = input_dir
        super().__init__(output_dir=output_dir)

    def extract_information(self, file_path):
        if file_path.lower().endswith('.xml'):
            xml_content = read_xml(file_path)
            return parse_disease(xml_content)
        else:
            return None

    def process_all_diseases(self):
        if self.input_dir is None:
            print("Error: No input directory provided for processing diseases.")
            return

        os.makedirs(self.output_dir, exist_ok=True)

        for file_name in os.listdir(self.input_dir):
            if file_name.lower().endswith(".xml"):
                file_path = os.path.join(self.input_dir, file_name)
                xml_content = read_xml(file_path)
                parsed_data = parse_disease(xml_content)

                output_filename = file_name.replace(".xml", ".json")
                output_path = os.path.join(self.output_dir, output_filename)

                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "parsed_data": parsed_data,
                    }, f, indent=2, ensure_ascii=False)

                print(f"Saved data to {output_path}")
