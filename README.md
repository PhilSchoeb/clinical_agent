# Clinical Agent - simple version of Agent Hospital: Project for IFT6289 - NLP with Deep Learning

Original work of Nhung Dang and Philippe Schoeb.

**DATA PREPROCESSING**

**Data**
All the data to test generation and evaluation patients can be found in the folder path_to_project/data_report

**To fetch data from MedLinePlus:**  
Run the following command in your terminal. The data will be automatically fetched and saved into the project folder:

```bash
python main.py fetch_data_from_medlineplus
```

**Clean the XML returned:**
All XML files need to be cleaned before proceeding to the next steps. Run the following command:

```bash
python main.py clean_xml_files_from_medlineplus
```
**Extract to json files**
```bash
python main.py process_disease_folder --input path_to_xml_folder --output path_to_json_folder
```
**GENERATION SYNTHETIC PATIENTS**
To generate synthetic patient profiles, navigate to the patient_generation folder and run the following command:
```bash
python patient_generation.py input_folder path_to_summary_folder output_folder path_to_output_folder \
    unique_diseases_file path_to_unique_diseases_file --num_patients NUM_PATIENTS --max_tries MAX_TRIES \
    --processed_log path_to_save_log
```
**Arguments:**

_input_folder: Folder containing disease files to process_

_path_to_summary_folder: Folder containing disease summary files (e.g., data_report/json_summary)_

_output_folder: Destination folder to save the generated patients_

_path_to_unique_diseases_file: Path to the unique disease file (e.g., data_report/resources/unique_diseases.txt)_

_--num_patients: (optional) Number of patients to generate per disease (default: 5)_

_--max_tries: (optional) Maximum retry attempts to generate valid profiles (default: 3)_

_--processed_log: (optional) Path to save the log file; if not specified, a log will be auto-generated in the project directory_

**EVALUATION SYNTHETIC PATIENTS**
To evaluate synthetic patient profiles using BERTScore, navigate to the patient_evaluation folder and run the following command:
```bash
python eval_patients_with_bertscore.py summary_dir path/to/summary_dir patient_dir path/to/patient_dir \
    output_csv results/evaluation.csv \
    --threshold 0.8 \
    --model_type yikuan8/Clinical-Longformer \
    --lang en \
    --num_layers 12
```
**Arguments:**

_summary_dir: Folder containing disease summary files (e.g., data_report/json_summary)_

_patient_dir: Folder with patient .json files (e.g., data_report/generated_patient)_

_results/evaluation.csv: output path for the evaluation result_

To evaluate synthetic patient profiles using cosine similarity, navigate to the patient_evaluation folder and run the following command:
```bash
python evaluate_patients_with_cosine.py \
    summary_dir path/to/summary_dir \
    patient_dir path/to/patient_dir \
    output_csv results/cosine_evaluation.csv \
    --threshold 0.8 \
    --top_k 3 \
    --model_name emilyalsentzer/Bio_ClinicalBERT
```
**Arguments:**
_summary_dir: Folder containing disease summary files (e.g., data_report/json_summary)_

_patient_dir: Folder with patient .json files (e.g., data_report/generated_patient)_

_output_csv: Output file to save cosine evaluation results_

_--threshold: (optional) Cosine threshold to mark a patient as Passable (default: 0.75)_

--top_k: (optional) Number of top-similarity sentences to average (default: 3)

--model_name: (optional) Name of the Sentence-BERT model used (default: emilyalsentzer/Bio_ClinicalBERT)

**TRAINING DOCTOR AGENT**

To train and evaluate the Doctor Agent, follow these steps using Google Colab:

1. Download the pretrained model. 
   Get the model from this link: https://drive.google.com/file/d/172iru3T088JpbQJF-cX6xPkucguVoZnp

2. Prepare the data 
   Ensure all required data is uploaded to Google Drive, and mount the Drive in Colab notebook.

3. Choose a simulation script
   Go to clinical_agent/experiment_scripts/Simulation_scripts, select the simulation script for your model, and open it in Google Colab.

4. Select the evaluation script
   Then go to clinical_agent/experiment_scripts/Real_life_eval_scripts and open the corresponding evaluation script in Colab.

5. Run the notebook
   Execute the cells from top to bottom: first run the simulation script, then the evaluation script to assess the results.

_Note: All data required for fine-tuning the model during simulation is provided in the section GENERATED SYNTHETIC PATIENTS DATASETS._

**GENERATED SYNTHETIC PATIENTS DATASETS**

This section contains all the synthetic patient profiles generated based on disease summaries. These profiles are used to simulate clinical scenarios for training and evaluating the Doctor Agent.

**Doctor Agent 1.0** 

Mistral_7B https://drive.google.com/drive/folders/1mzFomLn6wMei55EbyXfn7Ia-EiiXIv8s

Llama2_7B https://drive.google.com/drive/folders/1mwDH96PRNIZWkDm-Yrlav0iCvIjj8S4l

**Doctor Agent 2.0**

Llama3_8B_Instruct_Original https://drive.google.com/drive/folders/1vNljjl_i6oxSb9Oum8wfj7Hf4-ZyfN0F

**Doctor Agent 2.2**

Llama3_8B_Instruct_Original_And_Augmented https://drive.google.com/drive/folders/1YQes_qMYKW749XN8s9GoKZfYevuMkbU_

**Doctor Agent 3.0**
Llama3_8B_Instruct_Filtering_And_Augmented https://drive.google.com/drive/folders/1s56GJR5xxYgGRxzSeTS0HN8m40C4yMrP


