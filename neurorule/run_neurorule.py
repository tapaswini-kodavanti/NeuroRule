import os
import json
import argparse
import sys
import shutil
from pathlib import Path

def run_pipeline(dataset, interval, base_config_template, generate_synthetic=False, user_data=None, target_names=None):
    print(f"=== Starting NeuroRule Pipeline ===")
    print(f"Dataset Name: {dataset} | Split Interval: {interval}")

    # Establishing standardized internal directory structures
    dataset_dir = Path(f"data/{dataset}/datasets/{interval}")
    model_dir = Path(f"data/{dataset}/models/{interval}")
    weights_path = model_dir / "weights.pth"

    raw_data_path = dataset_dir / "raw.csv"
    processed_data_path = dataset_dir / "processed.csv"
    
    train_id_path = dataset_dir / "train" / "ID" / "data.csv"
    test_id_ood_path = dataset_dir / "test" / "ID+OOD" / "data.csv"
    test_id_path = dataset_dir / "test" / "ID" / "data.csv"
    test_ood_path = dataset_dir / "test" / "OOD" / "data.csv"

    # -------------------------------------------------------------------------
    # STEP 1: Process and Ingest Data File Path
    # -------------------------------------------------------------------------
    print("\n--- Step 1: Handling Dataset File ---")
    if user_data:
        user_data_path = Path(user_data)
        if user_data_path.exists():
            print(f"-> Ingesting external data from: {user_data}")
            train_id_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(user_data_path, raw_data_path)
            print(f"   Successfully copied data to internal pipeline path: {raw_data_path}")
        else:
            print(f"Error: The provided data file path '{user_data}' does not exist.")
            sys.exit(1)
    else:
        # If no explicit path is provided, run using default Breast Cancer dataset
        print(f"-> Using pre-existing Breast Cancer dataset: data/bc")

    # -------------------------------------------------------------------------
    # STEP 2: Split Data into ID / OOD Partitions
    # -------------------------------------------------------------------------
    print("\n--- Step 2: Perform ID / OOD Partitions ---")
    if not processed_data_path.exists():
        print(f"-> Preprocessing data into: {processed_data_path}")
        print(f"-> Performing ID / OOD data splits...")
        X_in, y_in, _, _ = split_id_ood_data(raw_data_path, processed_data_path, dataset_dir, target_names)

    # -------------------------------------------------------------------------
    # STEP 3: Process and Ingest Weights file path
    # -------------------------------------------------------------------------
    print("\n--- Step 3: Handling Model Weights ---")
        if not weights_path.exists():
            print("Training MLP network model...")
            model_dir.mkdir(parents=True, exist_ok=True)
            # TODO: train_mlp(dataset=dataset, save_path=str(weights_path))
            print(f"   Network trained. Saved weights internally to: {weights_path}")
        else:
            print(f"-> Using pre-existing weights found at: {weights_path}")

    # -------------------------------------------------------------------------
    # STEP 4: Generate Synthetic Data if Requested
    # -------------------------------------------------------------------------
    print("--- Step 4: Generating Synthetic Data ---")
    if generate_synthetic:
        print("Generating synthetic from base model...")
        # TODO: generate_synthetic_data(dataset=dataset, interval=interval, weights_file=weights_path)
    else:
        print("Synthetic data not requested. Skipping step.")

    # -------------------------------------------------------------------------
    # STEP 5: Dynamically Populating Configuration Template
    # -------------------------------------------------------------------------
    print("--- Step 5: Populating Config Template ---")
    with open(base_config_template, 'r') as f:
        config = json.load(f)
    
    dc = config["domain_config"]

    print("Reading input and output features")
    # TODO: inputs, outputs = read_features(processed_data_path)

    # TODO: Programmatically insert the following into the json file
    # inputs, outputs
    # target names
    # synthetic data file (refers to filtered data used in NeuroRule training)
    # raw_data_file (combined ID+ODD training data, represents baseline processed data)
    # in/out_distribution_data
    # experiment_id: dataset_test

    # Save transient/active JSON file for the framework to pick up
    temp_config_path = Path(f"configs/{dataset}/{interval}")
    temp_config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(temp_config_path, 'w') as f:
        json.dump(config, f, indent=4)
    print(f"-> Execution config written to temporary path: {temp_config_path}")

    # -------------------------------------------------------------------------
    # STEP 6: Launch Evolution Execution Loop
    # -------------------------------------------------------------------------
    print("\n--- Step 6: Starting NeuroRule Evolutionary Process ---")
    # TODO: review command cmd = f"python main_entry_point.py --config {temp_config_path}"
    print(f"Executing underlying repository command: {cmd}\n")
    
    exit_status = os.system(cmd)
    
    if exit_status == 0:
        print("\n=== NeuroRule Framework Pipeline Completed Successfully ===")
    else:
        print(f"\nPipeline execution aborted with status code: {exit_status}")
        sys.exit(exit_status)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated NeuroRule Orchestration Command Interface")
    
    # Core Pipeline Flags
    parser.add_argument('--dataset', type=str, required=True, help="Name of your dataset folder space (e.g., bc, heart_disease)")
    parser.add_argument('--interval', type=str, required=True, help="Threshold split tier indicator (e.g., 0.80)")
    parser.add_argument('--template', type=str, default="configs/neurorule_template.json", help="Path to base JSON template")
    parser.add_argument('--synthetic', type=bool, default=False, help="To generate and use synthetic data in training")
    
    # Paths to User Provided Files
    parser.add_argument('--data', type=str, default=None, help="Path to absolute/relative external data file (.csv)")
    parser.add_argument('--weights', type=str, default=None, help="Path to absolute/relative external model weights (.pth)")
    
    # Dynamic Classification Arrays
    parser.add_argument('--target-names', type=str, nargs="+", default=None, help="Space-separated array strings for mapping classifications labels")
    
    args = parser.parse_args()
    run_pipeline(
        dataset=args.dataset, 
        interval=args.interval, 
        base_config_template=args.template, 
        generate_synthetic=args.synthetic,
        user_data=args.data,
        target_names=args.target_names
    )