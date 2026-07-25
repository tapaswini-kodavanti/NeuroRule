import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn.preprocessing import StandardScaler

from model import MLP

# class MLP(nn.Module):
#     def __init__(self, input_dim, num_classes=2):
#         super().__init__()
#         self.net = nn.Sequential(
#             nn.Linear(input_dim, 32),
#             nn.ReLU(),
#             nn.Linear(32, 16),
#             nn.ReLU(),
#             nn.Linear(16, num_classes)
#         )

#     def forward(self, x):
#         return self.net(x)


### SYNTHESIS FUNCTIONS ###

def synthesize_data(X_df, numeric_cols, categorical_cols,
                            n_samples=5000, gamma=0.1, low_pct=1.0, high_pct=99.0,
                            random_state=None):
    
    def compute_bounds(X_df, numeric_cols, low_pct=1.0, high_pct=99.0, gamma=0.1):
        # X_df: pandas DataFrame of training data (raw/unscaled)
        mins = X_df[numeric_cols].quantile(low_pct/100.0).values
        maxs = X_df[numeric_cols].quantile(high_pct/100.0).values
        spans = maxs - mins
        # avoid zero spans
        spans[spans == 0] = 1e-6
        low = mins - gamma * spans
        high = maxs + gamma * spans
        return low, high

    rng = np.random.default_rng(random_state)
    low, high = compute_bounds(X_df, numeric_cols, low_pct=low_pct, high_pct=high_pct, gamma=gamma)
    n_num = len(numeric_cols)
    Xs_num = rng.uniform(low=low, high=high, size=(n_samples, n_num))

    # categorical: sample by empirical frequencies
    Xs_cat = {}
    for c in categorical_cols:
        vals, counts = np.unique(X_df[c].values, return_counts=True)
        probs = counts / counts.sum()
        picks = rng.choice(len(vals), size=n_samples, p=probs)
        Xs_cat[c] = vals[picks]

    # assemble DataFrame
    df_num = pd.DataFrame(Xs_num, columns=numeric_cols)
    df_cat = pd.DataFrame(Xs_cat)
    Xs = pd.concat([df_num, df_cat.reset_index(drop=True)], axis=1)[list(numeric_cols) + list(categorical_cols)]
    return Xs


# Generate synthetic data according to established distribution
def synthesize_to_distribution(X_df, model, scaler, target_dist, conf_threshold=0.8, n_total=1000):
    model.eval()

    X_scale = scaler.fit_transform(X_df)
    X_tensor = torch.tensor(X_scale, dtype=torch.float32)

    # Run through model
    with torch.no_grad():
        logits = model(X_tensor)
        probs = torch.softmax(logits, dim=1)
        confs, preds = torch.max(probs, dim=1)

    probs_np = probs.numpy()
    confs_np = confs.numpy()
    preds_np = preds.numpy()

    # Filter by confidence
    conf_mask = confs_np >= conf_threshold
    X_conf = X_df[conf_mask]
    probs_conf = probs_np[conf_mask]
    confs_conf = confs_np[conf_mask]
    preds_conf = preds_np[conf_mask]

    class_counts = {
        c: int(round(frac * n_total)) for c, frac in target_dist.items()
    }

    # Select top confident samples
    selected_idx = []
    for c, count in class_counts.items():
        idx_c = np.where(preds_conf == c)[0]
        if len(idx_c) == 0:
            print("something went wrong; no samples are above confidence threshold for class:", c)

        order = np.argsort(-confs_conf[idx_c])
        top_idx = idx_c[order[:count]]
        selected_idx.extend(top_idx)
    
    # Filter out records
    X_selected = pd.DataFrame(np.array(X_conf)[selected_idx])
    X_selected.columns = X_df.columns
    y_selected = preds_conf[selected_idx]
    probs_selected = probs_conf[selected_idx]

    return X_selected, y_selected, probs_selected

def get_distribution(y):
    unique, counts = np.unique(y, return_counts=True)
    total = len(y)
    dist = {u: c / total for u, c in zip(unique, counts)}
    return dist

def output_dataset(X_synth, y_synth, class_names, filename):
    X_synth = pd.DataFrame(X_synth, columns=X_synth.columns)
    y_synth = pd.get_dummies(y_synth)
    y_synth.columns = class_names

    # Force boolean columns in synthetic data to int
    bool_cols = X_synth.select_dtypes(include='bool').columns
    for col in bool_cols:
        X_synth[col] = X_synth[col].astype(int)

    synth_data = pd.concat([X_synth, y_synth], axis=1)
    
    synth_data.to_csv(filename, index=False)


def generate_synthetic_data(dataset_dir, model_dir, X_in, y_in, alpha=1.0, multiplier=200, conf_threshold=0.7):
    data_size = X_in.shape[0]
    num_samples = int(alpha * data_size)
    distribution_map = get_distribution(y_in.values.squeeze())
    numeric_cols = X_in.select_dtypes(include=[np.number]).columns
    categorical_cols = X_in.select_dtypes(exclude=[np.number]).columns

    input_dim = X_in.shape[1]
    num_classes = y_in.shape[1]


    X_tensor = torch.tensor(StandardScaler().fit_transform(X_in), dtype=torch.float32)
    y_tensor = torch.tensor(y_in.values.squeeze(), dtype=torch.long).argmax(dim=1) # not one-hot encoded

    weights_filename = model_dir / "weights.pth"
    if weights_filename:
        model = MLP(input_dim, num_classes)
        model.load_state_dict(torch.load(weights_filename))
        model.eval()
        predictions = model(X_tensor)

        _, predicted_classes = torch.max(predictions, 1)
        accuracy = (predicted_classes == y_tensor).float().mean()
        print(f"Final Training Accuracy: {accuracy.item()*100:.2f}%")
    else:
        print(f"Error: The provided weights file path '{weights_filename}' does not exist")

    X_synth_raw = synthesize_data(X_in, numeric_cols, categorical_cols, num_samples * multiplier, gamma=0.0)
    X_synth, y_synth, preds = synthesize_to_distribution(X_synth_raw, model, StandardScaler(), distribution_map, conf_threshold, num_samples)
    output_dataset(X_synth, y_synth, class_names, filename)

