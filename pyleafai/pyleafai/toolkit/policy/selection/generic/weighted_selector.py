
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

from pyleafai.toolkit.data.math.weightable import Weightable
from pyleafai.toolkit.data.math.weighted_entity import WeightedEntity

from pyleafai.api.policy.selection.selector import Selector

from pyleafai.toolkit.policy.math.weights import Weights
from pyleafai.toolkit.policy.math.weights_operations import WeightsOperations
from pyleafai.toolkit.policy.serialization.parsers.weights_parser \
    import WeightsParser


class WeightedSelector(Selector):
    """
    Selects a single element from a population  where the relative
    probability for choosing any element is specified as a list of
    weights.

    The weights in the list do not have to be normalized, they merely have
    to express the proportionality of the probabilities.
    """

    def __init__(self, random, weights_string=None, weights=None):
        """
        Constructor.

        :param random a Random number generator.
        :param weights: list of doubles representing the weights
                    of the elements. If this is None, we assume
                    that list of elements to select from are Weightables.
                    If they are not Weightables, we assume that all
                    elements have the same weight.
        :param weights_string: a string to be parsed that contains
                    the weights for the elements.  This is invoked
                    only if the weights passed in are None.
        """

        self._random = random

        use_weights = weights
        if use_weights is None and weights_string is not None:
            # Parse the passed in string
            weights_parser = WeightsParser()
            use_weights = weights_parser.parse(weights_string)

        if not isinstance(use_weights, Weights) and use_weights is not None:
            use_weights = Weights(use_weights)

        self._weights = use_weights

    def select(self, pool):
        """
        Fulfill the IndividualSelector interface.
        """

        next_double = self._random.next_double()
        return self.select_with_decision(pool, next_double)

    def select_with_decision(self, population, next_double):
        """
        Performs the meat of the select() function without the non-determinism
        of calling on the Random.

        :param population: the immutable collection to choose an element from
        :param next_double: the pre-decided random number to use in picking
                    the element from the distribution
        :return: a possibly empty Collection of a single distinct element from
                    the population, which is determined by the next_double
                    parameter and the distribution of weights for the population
        """

        if population is None or len(population) == 0:
            return []

        use_weights = self.determine_weights_to_use(population)

        # Use the WeightOperations to construct some other related
        # weightings from the original.
        ops = WeightsOperations()
        normalized_weights = ops.normalize(use_weights)
        search_me = ops.create_binary_searchable(normalized_weights)

        # Use the passed-in next_double random number to choose the element
        # according to the distribution
        index = ops.binary_search(search_me, next_double)
        chosen_one = population[index]

        # Conform to the Selector interface upon return
        selection = [chosen_one]
        return selection

    def determine_weights_to_use(self, population):
        """
        :param population: a non-empty list of homogenously typed elements
        :return: the Weights to use for this population
        """

        one_element = population[0]
        if isinstance(one_element, Weightable):
            # The population consists of Weightables, use the data there.
            return Weights(population)

        # Get the weights from what was passed in
        n_pop = len(population)
        n_weights = 0
        if self._weights is not None:
            n_weights = len(self._weights.get_weighted_entities())

        # Nothing to go on. Use equal weights for the population
        if n_weights == 0:
            fly_weights = []

            # Note: _ is pythonic for unused variable
            for _ in range(n_pop):
                fly_weights.append(1.0)
            return Weights(fly_weights)

        entities = self._weights.get_weighted_entities()

        # See if we have enough in the weights that were provided
        if n_pop <= n_weights:
            use_entities = entities[0:n_pop]
            return Weights(use_entities)

        # We do not have enough in the weights that were provided
        use_entities = list(entities)
        # Note: _ is pythonic for unused variable
        for _ in range(n_pop - n_weights):
            # For each extra, add a weight of 1.0
            new_entity = WeightedEntity(1.0, None)
            use_entities.append(new_entity)

        return Weights(use_entities)
