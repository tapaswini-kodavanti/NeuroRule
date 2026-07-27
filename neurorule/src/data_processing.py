import sys
import pandas as pd

# One-hot encodes data features
def split_id_ood_data(raw_data_path=None, processed_data_path=None, dataset_dir=None, class_names=None, interval=None):
    if not (raw_data_path and class_names):
        print(f"Error: The provided dataset does not exist.")
        sys.exit(1)

    # Load raw dataset
    dataset = pd.read_csv(raw_data_path)
    X = dataset.drop(columns=class_names)
    y = dataset[class_names]
    y.columns = class_names

    # Sort cateogorical and numerical features
    categorical_features = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    numeric_features = X.select_dtypes(include=["integer", "floating"]).columns.tolist()

    bool_cols = X.select_dtypes(include='bool').columns
    for col in bool_cols:
        X[col] = X[col].astype(int)

    # One-hot encode the X column
    df_encoded = dataset.copy()
    for c in categorical_features:
        df_encoded = pd.get_dummies(df_encoded, columns=[c], drop_first=False)

    # One-hot encode the y column 
    if len(class_names) == 1:
        for c in class_names:
            df_encoded = pd.get_dummies(df_encoded, columns=[c], drop_first=False)
        class_names = [col for col in df_encoded.columns if col.startswith(tuple(class_names))]

    # Save output
    df_encoded.to_csv(processed_data_path, index=False)

    X = df_encoded.drop(columns=class_names)
    y = df_encoded[class_names]
    y.columns = class_names



    ### Perform ID / OOD Splits
    def compute_shrunk_bounds(df, numeric_features, gamma=0.1, low_pct=1.0, high_pct=99.0):
        # df: raw data
        mins = df[numeric_features].quantile(low_pct/100.0).values
        maxs = df[numeric_features].quantile(high_pct/100.0).values
        spans = maxs - mins

        # avoid zero spans
        spans[spans == 0] = 1e-6
        low = mins + gamma * spans
        high = maxs - gamma * spans
        return low, high

    gamma = (1.0 - interval) / 2.0
    low_bounds, high_bounds = compute_shrunk_bounds(X, numeric_features, gamma)

    mask = pd.Series([True] * X.shape[0])
    for i, col in enumerate(numeric_features):
        mask &= (X[col] >= low_bounds[i]) & (X[col] <= high_bounds[i])

    # Do the shrinking
    X_in, y_in = X[mask], y[mask]
    X_out, y_out = X[~mask], y[~mask]

    X_in = X_in.reset_index(drop=True)
    y_in = y_in.reset_index(drop=True)

    # Save to file
    if dataset_dir:
        in_distribution_file = dataset_dir / "in_distribution.csv"
        out_distribution_file = dataset_dir / "out_of_distribution.csv"

        output_data = pd.concat([X_in, y_in], axis=1)
        output_data.to_csv(in_distribution_file, index=False)

        output_data = pd.concat([X_out, y_out], axis=1)
        output_data.to_csv(out_distribution_file, index=False)


    return X_in, y_in, class_names, X_out, y_out


def generate_input_output_schema(processed_data_path, dataset_name, target_names):
    """
    Inspects a processed CSV to generate the framework's 'inputs' and 'outputs' structures.
    """
    df = pd.read_csv(processed_data_path)

    # Separate features from target
    feature_cols = [col for col in df.columns if col not in target_names]
    # feature_cols = [col for col in df.columns if col != target_column]
    
    inputs_schema = []
    for col in feature_cols:
        dtype_str = "float"
        # Infer type based on pandas dtypes or uniqueness
        if df[col].dtype == 'bool' or set(df[col].dropna().unique()).issubset({0, 1, 0.0, 1.0}):
            dtype_str = "bool"
            
        inputs_schema.append({
            "name": col,
            "size": 1,
            "values": [dtype_str]
        })
        
    outputs_schema = [
        {
            "name": dataset_name + "_target",
            "size": len(target_names),
            "activation": "softmax" if len(target_names) > 1 else "sigmoid",
            "use_bias": True,
            "values": target_names
        }
    ]
    
    return inputs_schema, outputs_schema


def set_training_files(dataset_dir):
    test_id_ood_path = dataset_dir / "test" / "ID+OOD" / "data.csv"
    test_id_path = dataset_dir / "test" / "ID" / "data.csv"
    test_ood_path = dataset_dir / "test" / "OOD" / "data.csv"

    # Read OOD data
    ood_data_path = dataset_dir / "out_of_distribution.csv"
    if ood_data_path.exists():
        ood_df = pd.read_csv(ood_data_path)
        ood_df.to_csv(test_ood_path, index=False)

        # Combine ID and OOD for the combined test set
        test_df = pd.read_csv(test_id_path)
        combined_df = pd.concat([test_df, ood_df], axis=0)
        combined_df.to_csv(test_id_ood_path, index=False)

    # Clean up ID and OOD files
    in_distribution_file = dataset_dir / "in_distribution.csv"
    out_distribution_file = dataset_dir / "out_of_distribution.csv"
    if in_distribution_file.exists():
        in_distribution_file.unlink()
    if out_distribution_file.exists():
        out_distribution_file.unlink()