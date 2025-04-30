from lxml import etree
import re
from pathlib import Path

"""
This script defines an `XMLFolderCleaner` class that cleans XML files in bulk.

Main features:
- Removes unnecessary XML tags and attributes (e.g., <file>, <server>, 'url', 'rank').
- Strips HTML tags (e.g., <p>, <li>, <span>) and extra whitespace inside <content> elements.
- Writes cleaned XML files to a parallel directory structure.

This tool is useful for preprocessing XML data fetched from MedlinePlus before parsing or analysis.
"""


def clean_html_tags(text):
    # Remove tags for p, li, ul, span -- opening/closing/self-closing => replace with nothing
    cleaned = re.sub(r'</?(?:p|li|ul|span)(?:\s+[^>]*)?/?>', '', text, flags=re.IGNORECASE)

    # Remove all double quotes
    cleaned = cleaned.replace('"', '')

    # Remove any extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def remove_redundant_tags(tree: etree._ElementTree) -> etree._ElementTree:
    # 1. Remove 'url' and 'rank' attributes from <document> elements
    for doc_elem in tree.xpath("//document"):
        for attr in ['url', 'rank']:
            if attr in doc_elem.attrib:
                del doc_elem.attrib[attr]

    # 2. Remove <content name="organizationName"> elements
    removable_content_names = ["organizationName", "snippet"]
    for name in removable_content_names:
        for content_elem in tree.xpath(f"//content[@name='{name}']"):
            parent = content_elem.getparent()
            if parent is not None:
                parent.remove(content_elem)

    # 3. Remove <file>, <server>, <count>, <retstart>, <retmax> elements
    removable_tags = ["file", "server", "count", "retstart", "retmax"]
    for tag in removable_tags:
        for elem in tree.xpath(f"//{tag}"):
            parent = elem.getparent()
            if parent is not None:
                parent.remove(elem)

    return tree


class XMLFolderCleaner:
    def __init__(self):
        # TODO: Refactor code - Reuse in FetchHeartDiseaseData-fetch_data.py
        current_file = Path(__file__).resolve()  # Get the absolute path to this file
        project_root = current_file.parent.parent  # Get the project root
        # TODO: handle multiple cases here
        self.input_folder = project_root / "data" / "heart_diseases" / "xml"
        # self.input_folder = project_root / "data" / "infection_diseases" / "xml"
        if not self.input_folder.exists():
            raise FileExistsError(f"Input folder '{self.input_folder}' does not exist.")
        # TODO: handle multiple cases here
        self.output_folder = project_root / "data" / "heart_diseases" / "xml_cleaned"  # save to xml_cleaned folder
        # self.output_folder = project_root / "data" / "infection_diseases" / "xml_cleaned"
        self.output_folder.mkdir(parents=True, exist_ok=True)  # create folder
        if not self.output_folder.exists():
            raise FileExistsError(f"Unable to create '{self.output_folder}'.")

    def process(self):
        # Use rglob to traverse all subdirectories under self.input_folder
        for xml_file in self.input_folder.rglob("*.xml"):
            print(f"Processing: {xml_file}")

            # Parse the XML
            parser = etree.XMLParser(remove_blank_text=True, recover=True)
            tree = etree.parse(str(xml_file), parser)

            # Clean the <content> elements
            for content_elem in tree.xpath("//content"):
                if content_elem.text:
                    original_text = content_elem.text
                    cleaned_text = clean_html_tags(original_text)
                    content_elem.text = cleaned_text

            # Remove redundant tags
            tree = remove_redundant_tags(tree)

            # Figure out the relative path from input_folder
            relative_path = xml_file.relative_to(self.input_folder)
            # e.g. acute_rheumatic_fever/acute_rheumatic_endocarditis.xml

            # Construct the output file path under output_folder
            output_file = self.output_folder / relative_path

            # Ensure the subfolder exists in the output
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Save the cleaned XML
            tree.write(str(output_file), encoding="utf-8", xml_declaration=True, pretty_print=True)
            print(f"Cleaned XML saved to: {output_file}")
