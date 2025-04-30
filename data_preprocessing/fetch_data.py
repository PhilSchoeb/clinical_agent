import requests
import urllib.parse
from pathlib import Path
from utils.file_handler import write_to_xml

"""
This script defines the `FetchDiseaseData` class used to fetch disease-related
XML content from the MedlinePlus Health Topics API and save it locally.

It takes a list of disease terms, constructs appropriate query URLs,
retrieves XML responses, and writes them to a specified output folder.
"""


class FetchDiseaseData:
    def __init__(self):
        current_file = Path(__file__).resolve()  # Get the absolute path to this file
        project_root = current_file.parent.parent  # Get the project root
        self.output_folder = project_root / "data" / "heart_diseases" / "xml"  # Path to 'data/heart_diseases/xml'
        # self.output_folder = project_root / "data" / "infection_diseases" / "xml"  # Path to 'data/infection_diseases/xml'
        self.output_folder.mkdir(parents=True, exist_ok=True)  # create folder
        self.base_url = "https://wsearch.nlm.nih.gov/ws/query"

    def fetch_data(self, diseases_terms):
        count = 0
        for term in diseases_terms:
            encoded_term = urllib.parse.quote(term)  # URL-encode
            url = f"{self.base_url}?db=healthTopics&term={encoded_term}"  # Construct the full query URL
            response = requests.get(url)
            if response.status_code == 200:
                # Create a filename from the term
                filename = term.lower().replace(" ", "_") + ".xml"
                file_path = self.output_folder / filename
                write_to_xml(file_path, response)
                print(f"Saved XML for '{term}' under '{term}' => {filename}")
            else:
                print(f"Error {response.status_code} retrieving data for '{term}' in '{diseases_terms}'")
