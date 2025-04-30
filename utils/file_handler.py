import json
import pdfplumber
import os


def read_pdf(input_path):
    lines = []
    try:
        with pdfplumber.open(input_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    # Split on the newline characters
                    page_lines = text.split('\n')
                    lines.extend(page_lines)
    except Exception as e:
        print(f"Error reading PDF '{input_path}': {e}")
        return []

    return lines


def output_json(filename, text):
    try:
        with open(filename + ".json", "w") as json_file:
            json.dump(text, json_file, indent=4)
        print(f"JSON file '{filename}.json' created successfully.")
    except Exception as e:
        print(f"Error writing to {filename}.json: {e}")


def write_to_xml(file_path, content):
    # need to construct file_path before
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content.text)
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")


def read_terms_from_json(json_path):
    """
        Reads a JSON file where the data is a dictionary of lists.
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{json_path}' not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{json_path}'.")
        return []
    except Exception as e:
        print(f"Error reading '{json_path}': {e}")
        return []

    terms = []
    try:
        for key, term in data.items():
            if isinstance(term, list):
                term.append(key)
                terms.extend(term)
            else:
                print(f"Warning: Key '{key}' is not associated with a list.")
    except Exception as e:
        print(f"Error processing terms from '{json_path}': {e}")

    return terms


def read_json(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            json_dict = json.load(f)
        return json_dict
    except FileNotFoundError:
        print(f"Error: File '{json_path}' not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{json_path}'.")
        return {}
    except Exception as e:
        print(f"Error reading '{json_path}': {e}")
        return {}


def read_xml(file_path):
    """
    Reads the entire XML file as a string and returns it.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        return xml_content
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return ""
    except UnicodeDecodeError:
        print(f"Error: Cannot decode '{file_path}' as UTF-8.")
        return ""
    except Exception as e:
        print(f"Error reading '{file_path}': {e}")
        return ""


def read_txt(file_path):
    """
    Reads a .txt file and returns its content as a string.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().splitlines()
        return content
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


def read_txt_strip(file_path):
    """
    Reads a .txt file and returns its content as a string.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines()]
        return content
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
