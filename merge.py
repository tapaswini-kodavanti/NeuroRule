import pandas as pd
from pathlib import Path

def merge_experiment_stats(root_directory, output_filename="experiment_stats.csv"):
    root = Path(root_directory).resolve()
    all_dataframes = []

    # 1. Find all "experiment_stats.csv" files in the subdirectories
    # We look for them specifically within the subfolders, not the root
    for csv_file in root.rglob("experiment_stats.csv"):
        # Prevent the script from reading the output file if it already exists
        # if csv_file.name == output_filename:
        #     continue
            
        try:
            df = pd.read_csv(csv_file)
            all_dataframes.append(df)
            print(f"Read {csv_file.parent.name}/experiment_stats.csv")
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")

    if not all_dataframes:
        print("No CSV files found to merge.")
        return

    # 2. Concatenate all data into one DataFrame
    merged_df = pd.concat(all_dataframes, ignore_index=True)

    # 3. Drop duplicates
    # This keeps the first instance and removes any identical rows found later
    before_count = len(merged_df)
    merged_df.drop_duplicates(inplace=True)
    after_count = len(merged_df)

    # 4. Sort by generation (optional, but helpful for 1..200)
    if 'generation' in merged_df.columns:
        merged_df.sort_values(by='generation', inplace=True)

    # 5. Save to the root directory
    output_path = root.parent / output_filename
    merged_df.to_csv(output_path, index=False)
    
    print("---")
    print(f"Process complete!")
    print(f"Removed {before_count - after_count} duplicate rows.")
    print(f"Final file saved to: {output_path}")

if __name__ == "__main__":
    # Change this to the path where your numbered dirs and subdirs live
    parent = "/Users/tapaswinikodavanti/Desktop/Research/neurorule-syn-0.95/0.95/"
    # parent = "/Users/tapaswinikodavanti/Desktop/Research/neurorule-data-12/baseline-solutions/ID/0.80/"
    for i in range(1, 8):
        # directory = f"baseline-solutions/ID+synthetic/0.80/{i}/uci_diabetes_test"
        directory = f"{i}/uci_diabetes_test"
        merge_experiment_stats(f"{parent}{directory}")