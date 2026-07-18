import sys
import os
import torch

from leaf_common.candidates.constants import EXPERIMENTS_DIR

if EXPERIMENTS_DIR not in sys.path:
    sys.path.append(EXPERIMENTS_DIR)
    print(f"Directory being added to sys.path: {EXPERIMENTS_DIR}")

import numpy as np
from MLPModule import MLP
from sklearn.preprocessing import StandardScaler


# def uci_data_fitness(inputs, predictions, target_values):
def uci_data_fitness(predictions, target_values):
    # inputs is added here to keep it consistent in the evaluator class
    
    # if type(predictions[0]) == int:
    #     print("need to one-hot encode")
    #     pred_array = np.array(predictions)
    #     predictions = np.stack([pred_array == 0, pred_array == 1], axis=1)  # bools

    fitness = 0
    number_of_cases = len(target_values)
    if number_of_cases > 0:
        number_of_hits = \
            np.sum(np.array(target_values) == np.array(predictions))
        fitness = number_of_hits / number_of_cases
    return fitness

# def uci_nn_fitness(inputs, predictions, target_values):
def uci_nn_fitness(inputs, predictions, weights_filename, num_classes):
    model = MLP(input_dim=inputs.shape[1], num_classes=num_classes)

    # Load weights
    WEIGHTS_PATH = os.path.join(EXPERIMENTS_DIR, weights_filename)
    model.load_state_dict(torch.load(WEIGHTS_PATH))
    model.eval()

    input_tensor = torch.tensor(inputs, dtype=torch.float32)
    scaler = StandardScaler()
    input_tensor = torch.tensor(scaler.fit_transform(input_tensor), dtype=torch.float32)
    with torch.no_grad():
        outputs = model(input_tensor) # outputs are raw logits (N, 2)
        
    
    _, nn_predictions = torch.max(outputs, 1) 
    ruleset_tensor = torch.tensor(predictions, dtype=torch.int64)
    fitness_tensor = (nn_predictions == ruleset_tensor).float().mean()

    fitness = fitness_tensor.item()
        
    return fitness

    