import pandas as pd
import os


def merge_results():
    # Get all the process-specific CSV files
    file_names = [
        f for f in os.listdir("results/parallel") if f.startswith("results_process_")
    ]

    # Read and concatenate the DataFrames from each file
    df_list = [
        pd.read_csv(os.path.join("results/parallel", file_name))
        for file_name in file_names
    ]
    merged_df = pd.concat(df_list, ignore_index=True)

    # Write the merged DataFrame to the consolidated results file
    merged_df.to_csv("results/parallel/results.csv", index=False)

    # Clean up the process-specific files
    # for file_name in file_names:
    #     os.remove(os.path.join("results", file_name))


if __name__ == "__main__":
    merge_results()
