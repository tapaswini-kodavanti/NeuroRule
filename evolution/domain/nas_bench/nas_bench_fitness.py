import os
import numpy as np

# See nas_bench domain README.md for how to get these
from nasbench.api import ModelSpec          # pylint: disable=import-error
from nasbench.api import NASBench           # pylint: disable=import-error
from nasbench.api import OutOfDomainError   # pylint: disable=import-error

NASBENCH_TFRECORD = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'nasbench_only108.tfrecord')
lookup_table = NASBench(NASBENCH_TFRECORD)


def nas_bench_fitness(adjacency_matrix, ops):
    matrix = np.full((7, 7), False)
    idx = np.triu_indices(7, 1)
    matrix[idx] = adjacency_matrix
    ops = ['input'] + list(ops) + ['output']
    model_spec = ModelSpec(matrix=matrix, ops=ops)
    try:
        fitness = lookup_table.query(model_spec)['validation_accuracy']
    except OutOfDomainError:
        # Invalid architecture
        fitness = 0.0
    return fitness
