import pandas as pd

# One-hot encodes data features
def split_id_ood_data(raw_data_path=None, processed_data_path=None, dataset_dir=None, class_names=None):
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
    numeric_features = X.select_dtypes(include=["int64", "float64"]).columns.tolist()

    bool_cols = X.select_dtypes(include='bool').columns
    for col in bool_cols:
        X[col] = X[col].astype(int)


    # switch_features = ["Diabetes", "Hypertension"]
    # switch_features = ['FastingBS'] # actually a bool column
    # for feature in switch_features:
        # numeric_features.remove(feature)
        # categorical_features.append(feature)

    # print(X.head())
    # print(y.head())
    # print(class_names)

    # print(categorical_features)
    # print(numeric_features)

    # print("\nData loaded")

    # One-hot encode the column
    df_encoded = dataset.copy()
    for c in categorical_features:
        df_encoded = pd.get_dummies(df_encoded, columns=[c], drop_first=False)

    # Save output
    df_encoded.to_csv(processed_data_path, index=False)



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
    
    low_bounds, high_bounds = compute_shrunk_bounds(X, numeric_features)

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


    return X_in, y_in, X_out, y_out
