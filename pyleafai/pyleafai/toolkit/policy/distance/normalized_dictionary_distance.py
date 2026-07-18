
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

from pyleafai.api.policy.distance.distance import Distance

from pyleafai.toolkit.data.math.type_keywords import TypeKeywords

from pyleafai.toolkit.policy.distance.leaf_count_distance_registry \
    import LeafCountDistanceRegistry
from pyleafai.toolkit.policy.distance.dictionary_leaf_count_distance \
    import DictionaryLeafCountDistance
from pyleafai.toolkit.policy.distance.flattened_branch_distance_registry \
    import FlattenedBranchDistanceRegistry
from pyleafai.toolkit.policy.distance.flattened_dictionary_distance \
    import FlattenedDictionaryDistance


class NormalizedDictionaryDistance(Distance):
    """
    A measure of distance between two dictionaries.
    All fields distance are normalized to values between 0.0 and 1.0,
    and any distance from this class for the entire dictionary is also
    normalized.
    """

    def __init__(self, dictionary_spec,
                 flattened_branch_distance_registry=None,
                 leaf_count_distance_registry=None,
                 field_exponent=1.0):
        """
        Constructor.

        :param dictionary_spec: the EvolvedStructureSpec instance
                 representing the spec of the dictionary
        :param flattened_branch_distance_registry: An instantiation of
            FlattenedBranchDistanceRegistry data-class string to
            field Distance functions
        :param leaf_count_distance_registry: An instantiation of
            LeafCountDistanceRegistry for data-class string to
            leaf-node counting Distance function lookup.
        :param field_exponent: the exponent used in the distance function
            Uses a default field_exponent of 1.0.

            Normally in a distance calculation you'd want to add up all
            the squares of the component distances and take the square root
            of that, ala the Pythagorean Theorem.  We have a situation here
            where we assume that all of our compontent distances will be
            normalized (between 0.0 and 1.0), so squaring can actually
            emphasize differences between certain components representing
            enums and booleans over other components that actualy represent
            numbers.  To combat that de-emphasis of numbers, we tweak
            this notion of "Field Exponent" down from 2.0 (squaring),
            to something linear (1.0). Experimental.
        """

        # Use default implementations if we were not handed anything in args
        if leaf_count_distance_registry is None:
            leaf_count_distance_registry = LeafCountDistanceRegistry()

        if flattened_branch_distance_registry is None:
            flattened_branch_distance_registry = \
                FlattenedBranchDistanceRegistry(
                    leaf_count_distance_registry)

        self._leaf_counter = DictionaryLeafCountDistance(
                                    dictionary_spec,
                                    leaf_count_distance_registry)
        self._flattened_distance = FlattenedDictionaryDistance(
                                    dictionary_spec,
                                    flattened_branch_distance_registry,
                                    leaf_count_distance_registry)
        self._field_exponent = field_exponent

    def distance(self, obj_a, obj_b):
        """
        :param obj_a: one DictionaryType
        :param obj_b: another DictionaryType
        :return: some measure of distance between a and b
        """

        n_fields = self._leaf_counter.distance(obj_a, obj_b)
        all_values_squared = self._flattened_distance.distance(obj_a, obj_b)

        distance = math.pow(all_values_squared, 1.0 / self._field_exponent)
        normalized_distance = distance / n_fields

        return normalized_distance

    def get_point_class(self):
        return TypeKeywords.DICTIONARY
