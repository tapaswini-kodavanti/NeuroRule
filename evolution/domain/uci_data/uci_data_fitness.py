import numpy as np


def uci_data_fitness(predictions, target_values):
    fitness = 0
    number_of_cases = len(target_values)
    if number_of_cases > 0:
        number_of_hits = \
            np.sum(np.array(target_values) == np.array(predictions))
        fitness = number_of_hits / number_of_cases
    return fitness
