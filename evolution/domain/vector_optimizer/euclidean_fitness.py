import numpy as np


def euclidean_distance(candidate_vector, target):
    return np.sqrt(np.sum((target - candidate_vector) ** 2))
