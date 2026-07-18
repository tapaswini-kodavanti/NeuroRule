
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

import math

from pyleafai.toolkit.data.math.weighted_entity import WeightedEntity
from pyleafai.toolkit.policy.math.weights import Weights


class WeightsOperations():
    """
    A utility class that contains operations on Weights objects.
    """

    def normalize(self, weights):
        """
        :param weights: The Weights instance to normalize.
        :return: a new Weights instance where the weights stored there are
                a normalized version of the instance's current weights.
                This does *not* change what is stored in the argument
                weights instance at all.
        """

        # Find the overall running_sum of the components
        running_sum = 0.0
        for weighted_entity in weights.get_weighted_entities():
            component = weighted_entity.get_weight()
            if not math.isinf(component):
                running_sum += math.fabs(component)

        normalized = []
        for weighted_entity in weights.get_weighted_entities():

            component = weighted_entity.get_weight()
            normalized_component = 0.0
            if running_sum != 0.0:
                normalized_component = component / running_sum

            entity = weighted_entity.get_entity()
            normalized_weighted_entity = WeightedEntity(normalized_component,
                                                        entity)
            normalized.append(normalized_weighted_entity)

        new_weights = Weights(normalized)
        return new_weights

    def create_binary_searchable(self, weights):
        """
        :param weights: The Weights instance to make binary searchable.
        :return: a new Weights instance whose weights are binary searchable
                using this class's binary_search() method.  The idea is that
                the weights are normalized and converted to an ascending
                list (of the same size) going from 0.0 to 1.0 at the end.

                One should be able to pick a random number between 0.0 and 1.0
                and pass that number into binary_search() to find
                which list element was chosen per the weights.

                This does not change what is stored in passed in Weights
                instance at all.
        """

        normalized = self.normalize(weights)

        running_sum = 0.0
        binary_searchable = []
        for weighted_entity in normalized.get_weighted_entities():
            component = weighted_entity.get_weight()
            if not math.isinf(component):
                running_sum += component

            new_weighted_entity = WeightedEntity(running_sum,
                                                 weighted_entity.get_entity())
            binary_searchable.append(new_weighted_entity)

        new_weights = Weights(binary_searchable)
        return new_weights

    def binary_search(self, weights, key):
        """
        Performs a binary search over the existing weights for the given key,
        with a twist.

        Assumes that the Weights has been prepared with
        create_binary_searchable() above.

        :param weights: The Weights instance to make binary searchable.
        :param key: the key to search for as per Collections.binary_search()
        :return: either:
            (a) the index into the weights if the key actually exists in the
                weights
         or (b) the index at which the key would be inserted, if it were
                to exist
        """

        index = self.index_binary_search(weights, key)

        if index < 0:
            # Exact key not found.
            # Reverse the index per Collections.binary_search()
            # to find the insertion point
            index = -(index + 1)

        # Skip past any exact matches of the key, starting at
        # the index. This does two things:
        # 1) Any entry with a probability of 0.0 will be
        #    entirely skipped over
        # 2) This tips the exact match in favor of the next
        #    highest entry, which plays well with the fact that
        #    Random.nextDouble()'s distribution is [0.0, 1.0).
        entities = weights.get_weighted_entities()
        while index < len(entities) and \
                entities[index].get_weight() == key:
            index = index + 1

        return index

    def index_binary_search(self, weights, key):
        low_index = 0
        entities = weights.get_weighted_entities()
        high_index = len(entities) - 1

        while low_index <= high_index:
            mid_index = int((low_index + high_index) / 2)
            mid_value = entities[mid_index].get_weight()
            comparison = mid_value - key

            if comparison < 0:
                low_index = mid_index + 1
            elif comparison > 0:
                high_index = mid_index - 1
            else:
                # Found the key
                return mid_index

        # key was not found
        index = -(low_index + 1)
        return index
