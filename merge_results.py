import pandas as pd
import os


def merge_results(results_dir: str, prefix: str):
    """Takes a bunch of csv files in results_dir with a certain prefix and combines them into a single csv file.

    Args:
        results_dir (str): The directory where the csv files we want to merge are.
        Also where we will store the resulting results.csv file

        prefix (str): The prefix of the files we want to combine
    """
    # Get all the process-specific CSV files
    file_names = [f for f in os.listdir(results_dir) if f.startswith(prefix)]

    # Read and concatenate the DataFrames from each file
    df_list = [
        pd.read_csv(os.path.join(results_dir, file_name)) for file_name in file_names
    ]
    merged_df = pd.concat(df_list, ignore_index=True)

    # Write the merged DataFrame to the consolidated results file
    merged_df.to_csv(os.path.join(results_dir, "results.csv"), index=False)

    # Clean up the process-specific files
    # for file_name in file_names:
    #     os.remove(os.path.join("results", file_name))


if __name__ == "__main__":
    merge_results(results_dir="results/parallel", prefix="results_process_")
