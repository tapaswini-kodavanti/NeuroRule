from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np

from src.model import MLP



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


def train_model(X, y, dataset_dir, model_dir):
    X_train, y_train, X_test, y_test, _ = train_mlp(X, y, dataset_dir, model_dir)
    return X_train, y_train, X_test, y_test


def train_mlp(X, y, dataset_dir, model_dir):
    # Ready data
    X = pd.get_dummies(X, drop_first=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    input_dim = X.shape[1]
    num_classes = y.shape[1]
    print(f"Training MLP with input_dim={input_dim}, num_classes={num_classes}")
    model = MLP(input_dim, num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    train_df = pd.concat([X_train, y_train], axis=1)
    test_df = pd.concat([X_test, y_test], axis=1)
    train_df.to_csv(dataset_dir / "train" / "ID" / "data.csv", index=False)
    test_df.to_csv(dataset_dir / "test" / "ID" / "data.csv", index=False)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)  # "fit" learns the mean/variance of each feature
    X_test = scaler.transform(X_test)  # fit isn't necessary because the scaler already learned the features

    # Save original data for reference
    X_train_old = pd.DataFrame(X_train, columns=X.columns)
    X_test_old = pd.DataFrame(X_test, columns=X.columns)
    y_train_old = pd.DataFrame(y_train, columns=y.columns)
    y_test_old = pd.DataFrame(y_test, columns=y.columns)

    # Convert to PyTorch tensors
    X_train = torch.tensor(X_train, dtype=torch.float32)
    X_test = torch.tensor(X_test, dtype=torch.float32)
    y_train = torch.tensor(y_train.values.squeeze(), dtype=torch.long)
    y_test = torch.tensor(y_test.values.squeeze(), dtype=torch.long)

    print(X_train.shape, y_train.shape, X_test.shape, y_test.shape)

    # Training loop
    num_epochs = 100
    for epoch in range(num_epochs):
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train.argmax(dim=1)) # convert to class indicies
        loss.backward()     # backprop
        optimizer.step()    # update gradients

        print(f"Epoch {epoch+1}/{num_epochs}: loss {loss}")

    # Output test accuracy
    predictions = model(X_test)
    _, predicted_classes = torch.max(predictions, 1)
    accuracy = (predicted_classes == y_test.argmax(dim=1)).float().mean()
    print(f"Test Accuracy: {accuracy.item()*100:.2f}%")

    # Verify that weights can be saved
    if model_dir:
        torch.save(model.state_dict(), model_dir / "weights.pth")
        print("Model weights saved to " + str(model_dir / "weights.pth"))

    return X_train_old, y_train_old, X_test_old, y_test_old, scaler