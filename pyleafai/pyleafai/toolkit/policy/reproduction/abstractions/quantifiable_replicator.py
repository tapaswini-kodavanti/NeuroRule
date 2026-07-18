
# Copyright (C) 2020-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
#
# This software is a trade secret, and contains proprietary and confidential
# materials of Cognizant Digital Business Evolutionary AI.
# Cognizant Digital Business prohibits the use, transmission, copying,
# distribution, or modification of this software outside of the
# Cognizant Digital Business EAI organization.
#
# END COPYRIGHT


from pyleafai.toolkit.policy.reproduction.abstractions.quantifiable_operator \
    import QuantifiableOperator


class QuantifiableReplicator(QuantifiableOperator):
    '''
    An abstract convenience class which, given a QuantifiableOperator
    (that creates a single GeneticMaterial instance), knows how to create
    a number of instances from it, given an arbitrarily long list of parents.
    '''

    def __init__(self, operator,
                 max_offspring=QuantifiableOperator.ANY_NUMBER):
        '''
        Constructor.

        :param operator: the operator to use as a basis for replication.
        :param max_offspring: the maximum number of offspring desired from
                            this replicator.
        '''
        self._operator = operator
        self._max_offspring = max_offspring

    def create_from(self, parents, parent_metrics):
        return self.create_n_from(parents, parent_metrics, self.get_max_offspring())

    def create_n_from(self, parents, parent_metrics, num_offspring):
        '''
        :param parents: an immutable collection of GeneticMaterial to use as a
                        basis for generating offspring.
        :param parent_metrics: an immutable iterable collection of metrics
            associated with each respective parent.
        :param num_offspring: the maximum number of offspring desired in
                             the output list.
        :return: a collection of at most num_offspring GeneticMaterial by using
                the incoming list of parents as basis material for the
                underlying QuantifiableOperator.

        raises RuntimeException if num_offspring is ANY_NUMBER and
        the minimum number of parents required for the operator is 0
        (a Creator).
        '''

        #  a bad combo leading to a very large list
        if num_offspring == QuantifiableOperator.ANY_NUMBER and \
                self.get_min_parents() == 0:

            raise ValueError(
                "Trying to replicate an enormous list from a Creator")

        #  Create a place to put all our offspring for the multiple iterations
        all_offspring = []

        #  Initialize how much more is left to do.
        n_offspring_left = num_offspring

        #  Create an iterator that will loop through the list of parents once.
        n_parents = len(parents)
        parents_index = 0
        while parents_index < n_parents and n_offspring_left > 0:

            #  Make a place for the subset of parents to go.
            parents_sub_set = []
            metrics_sub_set = []

            #  Continue through the passed-in list of parents, adding them
            #  to the subset list until we have reached the parents quota
            #  for the operator.
            n_parents_left = self.get_min_parents()
            while parents_index < n_parents and n_parents_left > 0:

                parent = parents[parents_index]
                parents_sub_set.append(parent)

                if parent_metrics is not None and \
                        isinstance(parent_metrics, list):
                    metrics = parent_metrics[parents_index]
                    metrics_sub_set.append(metrics)

                parents_index = parents_index + 1
                n_parents_left = n_parents_left - 1

            #  If we did not satisfy the minimum requirements for the
            #  operator, don't call the operator with insufficient arguments.
            #  We're done.
            if n_parents_left > 0:
                break

            #  Create the offspring.
            offspring_sub_set = self._operator.create_from(parents_sub_set,
                                                           metrics_sub_set)

            #  Add the offspring to the list, up to the amount specified
            n_offspring = len(offspring_sub_set)
            offspring_index = 0
            while offspring_index < n_offspring and n_offspring_left > 0:

                offspring = offspring_sub_set[offspring_index]
                offspring_index = offspring_index + 1

                all_offspring.append(offspring)
                n_offspring_left = n_offspring_left - 1

        return all_offspring

    def get_min_parents(self):
        '''
        :return:  the minimum number of parents needed for self
                QuantifiableReplicator, which by definition is the minimum
                number of the passed-in operator.
        '''
        return self._operator.get_min_parents()

    def get_max_offspring(self):
        '''
        :return: the max offspring this QuantifiableReplicator can make.
        '''
        return self._max_offspring
