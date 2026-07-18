def one_max_fitness(candidate_vector):
    fitness = 0
    length = len(candidate_vector)
    for i in range(length):
        if candidate_vector[i]:
            fitness += 1
    return fitness
