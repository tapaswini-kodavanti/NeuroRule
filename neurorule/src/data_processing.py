import pandas as pd

# One-hot encodes data features
def preprocess_data(raw_data_path=None, processed_data_path=None, class_names=None):
    if not (raw_data_path and class_names):
        print(f"Error: The provided dataset does not exist.")
        sys.exit(1)

    # Load raw dataset
    dataset = pd.read_csv(raw_data_path)
    X = dataset.drop(columns=class_names)                                        # May need to undo one-hot encoding here...
    X = pd.get_dummies(X, drop_first=True)
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

# 