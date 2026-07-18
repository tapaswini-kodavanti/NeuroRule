
import numpy as np


def generate_vector(model):

    fixed_input = np.ones((1, 1))
    output = model.predict(fixed_input)
    generated_vector = output[0]
    return generated_vector


def generate_integer_vector(model):
    float_vector = generate_vector(model)
    return float_vector.round()
