import json
import time
import random
import re
import os
import glob
import requests
import argparse

from PatientCodeGenerator import PatientCodeGenerator

"""
   Generates synthetic patient profiles for a list of diseases,
   skipping any disease whose summary contains no mention of symptoms or signs,
   and retrying up to `max_tries` if no profile with symptoms is produced.
   """

class PatientProfileGenerator:


    def __init__(
        self,
        num_patients: int = 5,
        max_tries: int = 3,
        processed_log: str = "processed_files.log",
        unique_diseases_file: str = "../data/resources/unique_infection_diseases.txt"
    ):
        self.NUM_PATIENTS = num_patients
        self.MAX_TRIES = max_tries
        self.PROCESSED_LOG = processed_log
        self.UNIQUE_DISEASES_FILE = unique_diseases_file

    # ──────── Utilities ───────────────────────────────────────────────────────

    def read_txt(self, file_path: str) -> list[str]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().splitlines()
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            return []
        except Exception as e:
            print(f"An error occurred reading {file_path}: {e}")
            return []

    def slugify(self, title: str) -> str:
        slug = title.lower()
        slug = re.sub(r'\s+', '_', slug)
        slug = re.sub(r'[^\w_]', '', slug)
        return slug

    def llama_generate(self, prompt: str) -> str:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3:instruct",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7}
            }
        )
        data = resp.json()
        if "response" not in data:
            raise RuntimeError(f"Generation failed: {data}")
        return data["response"]

    # ──────── Summary Inspection ───────────────────────────────────────────────

    def _get_raw_summary(self, disease: dict) -> str:
        pd = disease.get('parsed_data', {})
        if isinstance(pd.get('titles'), list) and 'FullSummary' in pd['titles'][0]:
            return pd['titles'][0]['FullSummary']
        return disease.get('FullSummary', '')

    def summary_has_symptoms(self, disease: dict) -> bool:
        raw = self._get_raw_summary(disease)
        return bool(re.search(r"\b(symptom|sign)s?\b", raw, flags=re.IGNORECASE))

    # ──────── Prompt & Parsing ────────────────────────────────────────────────

    def create_patients_with_prompt(self, disease: dict) -> str:
        raw_summary = self._get_raw_summary(disease)
        pd = disease.get('parsed_data', {})
        correct_term = pd.get('term', disease.get('title', '')).strip()
        summary = re.sub(
            rf"\b{re.escape(correct_term)}\b",
            "this condition",
            raw_summary,
            flags=re.IGNORECASE
        )

        header = (
            "You are a medical domain expert specializing in synthetic patient profiles.\n"
            f"Based on the disease summary below, generate exactly {self.NUM_PATIENTS} distinct patient profiles.\n"
            "Each must be independent and follow this format:\n"
        )
        block = (
            "--- Profile {i} ---\n"
            "Full name:\nAge:\nGender:\nSymptoms:\n"
            "Symptom duration:\nRecent travel history:\nMedical history:\n"
        )
        prompt = header + "\n".join(block.format(i=i+1) for i in range(self.NUM_PATIENTS))
        prompt += (
            "\nGuidelines:\n"
            "1. Do not mix information between profiles.\n"
            "2. Avoid any direct mention of the disease name.\n"
            "3. Use realistic, culturally diverse names; if two collide, tweak one’s age by ±1.\n"
            "4. Stick exactly to the field order and separators.\n\n"
            f"Summary:\n{summary}"
        )
        return self.llama_generate(prompt)

    def split_profiles(self, raw_output: str) -> list[str]:
        parts = re.split(r"^--- Profile \d+ ---\s*", raw_output, flags=re.MULTILINE)
        return [p.strip() for p in parts if p.strip()]

    def append_additional_info(self, text: str, disease: dict) -> str:
        all_d = self.read_txt(self.UNIQUE_DISEASES_FILE)
        correct = disease.get('term', disease.get('title', '')).strip()
        cause = disease.get('cause_diagnosis', '')

        others = [d for d in all_d if d.strip() and d.strip() != correct]
        mixed = random.sample(others, min(4, len(others))) + [correct]
        random.shuffle(mixed)

        text += "\nMixed diseases:\n"
        for d in mixed:
            text += f"- {d}\n"
        text += f"\nCorrect disease: {correct}\nDiagnosis cause: {cause}\n"
        return text

    def extract_result_under_json(self, generated_patient: str) -> dict:
        keys = [
            "Full name", "Age", "Gender", "Symptoms",
            "Symptom duration", "Recent travel history", "Medical history"
        ]
        extra = ["Mixed diseases", "Correct disease", "Diagnosis cause"]
        data = {}
        lines = generated_patient.splitlines()

        for key in keys:
            data[key] = ""
            for ln in lines:
                if ln.strip().startswith(key + ":"):
                    data[key] = ln.split(":", 1)[1].strip()
                    break

        for key in extra:
            if key == "Mixed diseases":
                data[key] = []
                for i, ln in enumerate(lines):
                    if ln.strip().startswith(key + ":"):
                        j = i + 1
                        while j < len(lines) and lines[j].strip().startswith("-"):
                            data[key].append(lines[j].lstrip("-").strip())
                            j += 1
                        break
            else:
                data[key] = ""
                for ln in lines:
                    if ln.strip().startswith(key + ":"):
                        data[key] = ln.split(":", 1)[1].strip()
                        break

        return data

    # ──────── File I/O ────────────────────────────────────────────────────────

    def read_diseases_from_json_file(self, path: str) -> list[dict]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("parsed_data", {}).get("titles", [])

    def write_generated_patients_to_json(self, disease: dict, patient_list: list[dict], out_folder: str):
        slug = self.slugify(disease.get("cause_diagnosis", disease.get("title", "")))
        final = os.path.join(out_folder, f"patients_{slug}.json")
        tmp = final + ".temp"
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(patient_list, f, indent=2, ensure_ascii=False)
        os.replace(tmp, final)
        print(f"Saved {len(patient_list)} profiles to {final}")

    def load_processed_files(self) -> set[str]:
        if os.path.exists(self.PROCESSED_LOG):
            with open(self.PROCESSED_LOG, "r", encoding="utf-8") as f:
                return set(f.read().splitlines())
        return set()

    def log_processed_file(self, fn: str):
        with open(self.PROCESSED_LOG, "a", encoding="utf-8") as f:
            f.write(fn + "\n")

    # ──────── Core Generation Logic ───────────────────────────────────────────

    def generate_for_each_diagnosis(self, diseases_list: list[dict]) -> tuple[list[dict], dict | None]:
        all_generated = []
        last_disease = None

        for disease in diseases_list:
            title = disease.get("title", "[no title]")
            if not self.summary_has_symptoms(disease):
                print(f" No symptoms or signs mentioned in summary for “{title}” – skipping.")
                continue

            print(f"→ Generating {self.NUM_PATIENTS} profiles for {title}")
            tries = 0
            success = False

            while tries < self.MAX_TRIES:
                raw = self.create_patients_with_prompt(disease)
                blocks = self.split_profiles(raw)
                profiles = []

                for blk in blocks:
                    with_meta = self.append_additional_info(blk, disease)
                    pdata = self.extract_result_under_json(with_meta)
                    if pdata.get("Symptoms"):
                        pdata["patient_number"] = PatientCodeGenerator().generate_patient_code()
                        profiles.append(pdata)

                if profiles:
                    all_generated.append({
                        "disease": title,
                        "patients": profiles
                    })
                    last_disease = disease
                    success = True
                    break
                else:
                    tries += 1
                    print(f"No valid profiles with symptoms for “{title}” – retry {tries}/{self.MAX_TRIES}")

            if not success:
                print(f"Skipping “{title}” after {self.MAX_TRIES} unsuccessful tries.")

        return all_generated, last_disease

    def run(self, input_folder: str, output_folder: str, unique_diseases_file: str):
        # override unique diseases file if provided
        self.UNIQUE_DISEASES_FILE = unique_diseases_file
        start = time.time()
        print("Start generating patients:", time.ctime(start))

        os.makedirs(output_folder, exist_ok=True)
        processed = self.load_processed_files()
        json_files = [
            f for f in glob.glob(os.path.join(input_folder, "*.json"))
            if not os.path.basename(f).startswith("patients_")
        ]

        for idx, jf in enumerate(json_files, start=1):
            if jf in processed:
                print(f"{idx}. Skipping already processed: {jf}")
                continue

            print(f"{idx}. Processing {jf} …")
            try:
                diseases = self.read_diseases_from_json_file(jf)
                gen_list, last = self.generate_for_each_diagnosis(diseases)
                if gen_list:
                    self.write_generated_patients_to_json(last, gen_list, output_folder)
                self.log_processed_file(jf)
            except Exception as e:
                print(f"Error processing {jf}: {e}")

        end = time.time()
        print("Finished:", time.ctime(end), f"({end - start:.2f}s elapsed)")


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic patient profiles for diseases.")
    parser.add_argument('input_folder', help='Path to input JSON folder')
    parser.add_argument('output_folder', help='Path to output JSON folder')
    parser.add_argument('unique_diseases_file', help='Path to unique diseases text file')
    parser.add_argument('--num_patients', type=int, default=5, help='Number of patients per disease')
    parser.add_argument('--max_tries', type=int, default=3, help='Max retry attempts per disease')
    parser.add_argument('--processed_log', default='processed_files.log', help='Path to processed log file')
    args = parser.parse_args()

    generator = PatientProfileGenerator(
        num_patients=args.num_patients,
        max_tries=args.max_tries,
        processed_log=args.processed_log,
        unique_diseases_file=args.unique_diseases_file
    )
    generator.run(args.input_folder, args.output_folder, args.unique_diseases_file)

if __name__ == '__main__':
    main()
