import subprocess
import os
import argparse
import sys
import shutil
from pathlib import Path

# Fix sys.path BEFORE importing any submodules
ROOT_DIR = Path(__file__).resolve().parent.parent
submodules = ["leaf-common", "evolution", "esp-sdk", "evolution-service", "pyleafai"]

for sub in submodules:
    sub_path = str(ROOT_DIR / sub)
    if sub_path not in sys.path:
        sys.path.insert(0, sub_path)

current_pythonpath = os.environ.get("PYTHONPATH", "")
new_paths = ":".join([str(ROOT_DIR / sub) for sub in submodules])
os.environ["PYTHONPATH"] = f"{new_paths}:{current_pythonpath}"




from src.data_processing import split_id_ood_data, generate_input_output_schema, set_training_files
from src.training import train_model
from src.synthetic_data_generator import generate_synthetic_data
from src.config_generator import generate_neurorule_config

def run_pipeline(dataset, interval, generate_synthetic=False, user_data=None, target_names=None):
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

    synthetic_data_path = dataset_dir / "train" / "synthetic" / "data.csv"

    # -------------------------------------------------------------------------
    # STEP 1: Process and Ingest Data File Path
    # -------------------------------------------------------------------------
    print("\n--- Step 1: Handling Dataset File ---")
    if user_data:
        user_data_path = Path(user_data)
        if user_data_path.exists():
            print(f"-> Ingesting external data from: {user_data}")
            train_id_path.parent.mkdir(parents=True, exist_ok=True)
            test_id_ood_path.parent.mkdir(parents=True, exist_ok=True)
            test_id_path.parent.mkdir(parents=True, exist_ok=True)
            test_ood_path.parent.mkdir(parents=True, exist_ok=True)
            synthetic_data_path.parent.mkdir(parents=True, exist_ok=True)

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
    # if not processed_data_path.exists():
    print(f"-> Preprocessing data into: {processed_data_path}")
    print(f"-> Performing ID / OOD data splits...")
    X_in, y_in, target_names, _, _ = split_id_ood_data(raw_data_path, processed_data_path, dataset_dir, target_names, interval)

    # -------------------------------------------------------------------------
    # STEP 3: Process and Ingest Weights file path
    # -------------------------------------------------------------------------
    print("\n--- Step 3: Handling Model Weights ---")
    if not weights_path.exists():
        print("Training MLP network model...")
        model_dir.mkdir(parents=True, exist_ok=True)
        train_model(X_in, y_in, model_dir=model_dir, dataset_dir=dataset_dir)
        print(f"   Network trained. Saved weights internally to: {weights_path}")
        set_training_files(dataset_dir)
    else:
        print(f"-> Using pre-existing weights found at: {weights_path}")

    # -------------------------------------------------------------------------
    # STEP 4: Generate Synthetic Data if Requested
    # -------------------------------------------------------------------------
    print("--- Step 4: Generating Synthetic Data ---")
    if generate_synthetic:
        print("Generating synthetic from base model...")
        generate_synthetic_data(dataset_dir=dataset_dir, model_dir=model_dir, X_in=X_in, y_in=y_in, class_names=target_names)
    else:
        print("Synthetic data not requested. Skipping step.")

    # -------------------------------------------------------------------------
    # STEP 5: Dynamically Populating Configuration Template
    # -------------------------------------------------------------------------
    print("--- Step 5: Populating Config Template ---")
    print("Reading input and output features")
    inputs, outputs = generate_input_output_schema(processed_data_path, dataset, target_names)

    temp_config_path = Path(f"configs/{dataset}/{interval}")
    if generate_synthetic:
        temp_config_file = temp_config_path / str(dataset + "_synthetic_config.json")
    else:
        temp_config_file = temp_config_path / str(dataset + "_config.json")

    generate_neurorule_config(
        template_path="configs/neurorule_template.json",
        output_config_path=temp_config_file,
        dataset_name=dataset,
        interval=interval,
        inputs_schema=inputs,
        outputs_schema=outputs,
        target_names=target_names,
        use_synthetic_data=generate_synthetic,
    )

    # Save transient/active JSON file for the framework to pick up
    print(f"-> Execution config written to temporary path: {temp_config_path}")

    # -------------------------------------------------------------------------
    # STEP 6: Launch Evolution Execution Loop
    # -------------------------------------------------------------------------
    print("\n--- Step 6: Starting NeuroRule Evolutionary Process ---")

    # Build absolute paths for PYTHONPATH
    abs_submodule_paths = [str((ROOT_DIR / sub).resolve()) for sub in submodules]
    
    # Copy current environment and update PYTHONPATH explicitly
    custom_env = os.environ.copy()
    existing_pythonpath = custom_env.get("PYTHONPATH", "")
    custom_env["PYTHONPATH"] = ":".join(abs_submodule_paths) + (f":{existing_pythonpath}" if existing_pythonpath else "")

    result = subprocess.run([sys.executable, "../evolution/app/evolve.py", "-p", str(temp_config_file)])
    exit_status = result.returncode
    
    if exit_status == 0:
        print("\n=== NeuroRule Framework Pipeline Completed Successfully ===")
    else:
        print(f"\nPipeline execution aborted with status code: {exit_status}")
        sys.exit(exit_status)


if __name__ == "__main__":
    ## Parse command-line arguments for the pipeline
    parser = argparse.ArgumentParser(description="Automated NeuroRule Orchestration Command Interface")
    
    # Core Pipeline Flags
    parser.add_argument('--dataset', type=str, required=True, help="Name of your dataset folder space (e.g., bc, heart_disease)")
    parser.add_argument('--interval', type=float, required=True, help="Threshold split tier indicator (e.g., 0.80)")
    parser.add_argument('--synthetic', action='store_true', default=False, help="To generate and use synthetic data in training")
    
    # Paths to User Provided Files
    parser.add_argument('--data', type=str, default=None, help="Path to absolute/relative external data file (.csv)")
    parser.add_argument('--weights', type=str, default=None, help="Path to absolute/relative external model weights (.pth)")
    
    # Dynamic Classification Arrays
    parser.add_argument('--target-names', type=str, nargs="+", default=None, help="Space-separated array strings for mapping classifications labels")
    
    args = parser.parse_args()
    run_pipeline(
        dataset=args.dataset, 
        interval=args.interval, 
        generate_synthetic=args.synthetic,
        user_data=args.data,
        target_names=args.target_names
    )