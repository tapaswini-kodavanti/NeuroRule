import json
import re
import pandas as pd
from pathlib import Path

def generate_neurorule_config(
    template_path: str,
    output_config_path: str,
    dataset_name: str,
    interval: str,
    inputs_schema: list[dict],
    outputs_schema: list[dict],
    target_names: list[str],
    user_weights_path: str = None
):
    """
    Programmatically builds a complete NeuroRule JSON configuration.
    
    Injects:
    1. 'inputs' & 'outputs' schema generated dynamically from the dataset.
    2. 'target_names' array.
    3. File paths (synthetic_data_file, weights_file, raw_data_file, ID/OOD data).
    4. 'experiment_id' string formatted as 'uci_{dataset_name}_test'.
    """
 

    # -------------------------------------------------------------------------
    # 1. LOAD TEMPLATE (HANDLING COMMENTS SAFEGUARDS)
    # -------------------------------------------------------------------------
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Strip non-standard JSON comments (# or //) if present in template
    content = re.sub(r'#.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    config = json.loads(content)

    # -------------------------------------------------------------------------
    # 2. CONSTRUCT DYNAMIC PATHS
    # -------------------------------------------------------------------------
    weights_file = user_weights_path or f"data/{dataset_name}/models/{interval}/weights.pth"
    synthetic_data_file = f"data/{dataset_name}/datasets/{interval}/train/ID/data.csv"
    raw_data_file = f"data/{dataset_name}/datasets/{interval}/test/ID+OOD/data.csv"
    in_dist_file = f"data/{dataset_name}/datasets/{interval}/test/ID/data.csv"
    out_dist_file = f"data/{dataset_name}/datasets/{interval}/test/OOD/data.csv"

    # -------------------------------------------------------------------------
    # 3. INJECT VALUES INTO JSON STRUCTURE
    # -------------------------------------------------------------------------
    # Inject inputs and outputs inside network block
    config["network"]["inputs"] = inputs_schema
    config["network"]["outputs"] = outputs_schema

    # Inject domain_config details
    dc = config["domain_config"]
    dc["data_set"] = f"load_{dataset_name}"
    dc["target_names"] = target_names
    dc["synthetic_data_file"] = synthetic_data_file
    dc["weights_file"] = weights_file
    dc["raw_data_file"] = raw_data_file
    dc["in_distribution_data"] = in_dist_file
    dc["out_of_distribution_data"] = out_dist_file

    # Inject experiment_id formatted as "uci_{dataset}_test"
    config["LEAF"]["experiment_id"] = f"uci_{dataset_name}_test"

    # -------------------------------------------------------------------------
    # 4. WRITE OUT ACTIVE CONFIG
    # -------------------------------------------------------------------------
    output_path = Path(output_config_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=4)
        
    print(f"Config generated successfully at: {output_path}")
    return config