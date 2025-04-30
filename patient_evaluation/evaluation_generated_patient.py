import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

"""
This script visualizes evaluation scores (Cosine Similarity and BERTScore) for 
synthetic patient profiles. It reads a CSV file containing patient-level metrics 
and generates three plots: a scatter plot to show correlation between the two metrics, 
a combined boxplot for metric comparison, and separate boxplots for distribution analysis. 
All plots are saved to a specified output folder.
"""


def read_scores_from_csv(file_path):
    df = pd.read_csv(file_path)
    if not {'PatientID', 'Cosine Similarity', 'BERTScore'}.issubset(df.columns):
        raise ValueError("CSV must contain columns: 'PatientID', 'Cosine Similarity', 'BERTScore'")
    return df


def plot_scatter(df, output_folder):
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x='Cosine Similarity', y='BERTScore', data=df, alpha=0.5)
    plt.title('Scatter Plot: Generated Patient vs. Full Summary')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "scatter_cosine_vs_bertscore.png"))
    plt.close()


def plot_mean_boxplot(df, output_folder):
    df_melted = df.melt(id_vars="PatientID", var_name="Metric", value_name="Score")
    plt.figure(figsize=(8, 6))
    sns.boxplot(x='Metric', y='Score', data=df_melted)
    plt.title("Box Plot of Mean Cosine Similarity and BERTScore")
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "boxplot_mean_metrics.png"))
    plt.close()


def plot_individual_boxplots(df, output_folder):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    sns.boxplot(y='Cosine Similarity', data=df, ax=axes[0])
    axes[0].set_title("Distribution of Cosine Similarity")

    sns.boxplot(y='BERTScore', data=df, ax=axes[1])
    axes[1].set_title("Distribution of BERTScore")

    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "boxplot_score_distribution.png"))
    plt.close()


def main():
    input_csv_path = "Synthetic_Patient_Evaluation_Scores.csv"
    output_folder = "generated_patient_plots"
    os.makedirs(output_folder, exist_ok=True)

    # Step 1: Read data
    df = read_scores_from_csv(input_csv_path)

    # Step 2: Create plots
    plot_scatter(df, output_folder)
    plot_mean_boxplot(df, output_folder)
    plot_individual_boxplots(df, output_folder)

    print(f"Plots successfully saved in: {output_folder}/")


if __name__ == "__main__":
    main()
