def leading_ones_fitness(candidate_vector):
    fitness = 0
    length = len(candidate_vector)
    while fitness < length and candidate_vector[fitness]:
        fitness += 1
    return fitness
