import matplotlib

matplotlib.use('TkAgg')
import pandas as pd
import matplotlib.pyplot as plt


def plot_scatter_and_boxplot(csv_file):
    """
    Load the CSV file and create:
      - A scatter plot of BERT scores for "Passable" and "Unpassable" patients.
      - A boxplot of BERT score distributions for each group.
    The CSV is assumed to have the following columns:
      - patient_id, bert_score, result
    """
    # Load the CSV file into a DataFrame
    data = pd.read_csv(csv_file)

    # Reset index for plotting if needed
    data = data.reset_index()

    # Separate data for each group
    passable = data[data["result"] == "Passable"]
    unpassable = data[data["result"] == "Unpassable"]

    # ----- Scatter Plot -----
    plt.figure()
    plt.scatter(passable["index"], passable["bert_score"],
                label="Bert_score > =0.8", alpha=0.7, color="#639cd9")
    plt.scatter(unpassable["index"], unpassable["bert_score"],
                label="Bert_score < 0.8", alpha=0.7, color="orange")
    plt.xlabel("Patient Index")
    plt.ylabel("BERT Score")
    plt.title("Scatter Plot of BERT Scores")
    plt.legend()
    plt.savefig("scatter_plot.png")

    # ----- Boxplot -----
    plt.figure()
    data_to_plot = [passable["bert_score"], unpassable["bert_score"]]
    plt.boxplot(data_to_plot, labels=["Passable", "Unpassable"])
    plt.ylabel("BERT Score")
    plt.title("Boxplot of BERT Score Distributions")
    # plt.show()
    plt.savefig("mean.png")


if __name__ == '__main__':
    csv_path = "eval_bertscore_infection_diseases.csv"
    plot_scatter_and_boxplot(csv_path)
