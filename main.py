import argparse
from data_preprocessing.extractor_factory import get_extractor_for_file
from data_preprocessing.fetch_data import FetchDiseaseData
from pathlib import Path
from data_preprocessing.xml_files_cleaner import XMLFolderCleaner
from utils.file_handler import read_txt
from data_preprocessing.disease_detail_extractor import DetailDiseaseExtractor


################################################################################
#######   MAIN FUNCTION -  PARSER SUBCOMMANDS  #################################
################################################################################
def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # DEFINE SUBCOMMANDS

    # Subcommand: pdf2json
    parser_pdf2json = subparsers.add_parser("pdf2json")
    parser_pdf2json.add_argument("--input", required=True, help="PDF file to extract")
    parser_pdf2json.add_argument("--output", required=True, help="Directory to save extracted data")

    # Subcommand: fetch_data_from_medlineplus
    subparsers.add_parser("fetch_data_from_medlineplus")

    # Subcommand: clean downloaded xml_files from medlineplus
    subparsers.add_parser("clean_xml_files_from_medlineplus")

    # Subcommand: process an entire folder of diseases (xml_cleaned)
    parser_process_diseases = subparsers.add_parser("process_disease_folder")
    parser_process_diseases.add_argument("--input", required=True, help="Root folder containing disease subfolders")
    parser_process_diseases.add_argument("--output", required=True, help="Folder to save JSON outputs")

    args = parser.parse_args()
    execute_sub_command(args)



################################################################################
################# EXECUTION DES SUB COMMANDES   ################################
################################################################################
def execute_sub_command(args):
    if args.command == "pdf2json":
        extract_heart_disease(args.input, args.output)
    elif args.command == "fetch_data_from_medlineplus":
        fetch_data_heart_disease()
    elif args.command == "clean_xml_files_from_medlineplus":
        clean_xml_files_from_medlineplus()
    elif args.command == "process_disease_folder":
        process_disease_folder(args.input, args.output)
    else:
        print("Unknown command. Use --help for usage.")
        return


################################################################################
#######   EXECUTION FUNCTIONS   ################################################
################################################################################
def extract_heart_disease(input_file, output_path):
    """
    Extracts data from the specified PDF (ex. heart disease codes) and saves to JSON.
    """
    extractor = get_extractor_for_file(input_file, output_path)  # Get the right extractor based on the file name
    extractor.process_file(input_file)  # Process the file (extract + save JSON)


def fetch_data_heart_disease():
    # Get the path to the JSON file
    current_file = Path(__file__).resolve()
    project_root = current_file.parent
    file_path = project_root / "data" / "resources" / "heart_diseases" / "heart_disease_list.txt"

    # fetch data from terms
    heart_diseases_dict = read_txt(file_path)
    # print(heart_diseases_dict)
    FetchDiseaseData().fetch_data(heart_diseases_dict)


def clean_xml_files_from_medlineplus():
    XMLFolderCleaner().process()


def process_disease_folder(input_dir, output_dir):
    """
    Uses DetailDiseaseExtractor to process an entire folder of diseases (xml_cleaned).
    Each subfolder = one disease; each subfolder has multiple .xml files.
    Output is one JSON per subfolder.
    """
    extractor = DetailDiseaseExtractor(input_dir=input_dir, output_dir=output_dir)
    extractor.process_all_diseases()


###############################
if __name__ == "__main__":
    main()
