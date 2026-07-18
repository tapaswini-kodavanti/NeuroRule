
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

from pyleafai.toolkit.policy.distance.dictionary_leaf_count_distance \
    import DictionaryLeafCountDistance
from pyleafai.toolkit.policy.distance.constant_distance \
    import ConstantDistance


class FlattenedDictionaryDistance(Distance):
    """
    A measure of distance between two dictionaries where the entire
    tree of the dictionary is flattened -- this is to say, every leaf
    node is treated with the same weight in the distance calculation.

    All leaf field distances are expected to be normalized to values
    between 0.0 and 1.0.

    Worth noting that this implementation only takes into account keys
    that are specified in the EvolvedStructureSpec. If there are extra
    keys, they are not counted at all towards the distance because
    we don't have information enough to know their depth.
    """
    NORMALIZED_MAX = ConstantDistance.DEFAULT_DISTANCE

    def __init__(self, dictionary_spec,
                 flattened_branch_distance_registry,
                 leaf_count_distance_registry,
                 field_exponent=1.0):
        """
        Constructor.

        :param dictionary_spec: the EvolvedStructureSpec instance
                 representing the spec of the dictionary
        :param flattened_branch_distance_registry: An instantiation of
            FlattenedBranchDistanceRegistry.
        :param leaf_count_distance_registry:
            a DistanceFunctionRegistry for data-class string to
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

        self._distance_functions = flattened_branch_distance_registry

        self._field_exponent = field_exponent

        self._leaf_count_distance = DictionaryLeafCountDistance(
                                            dictionary_spec,
                                            leaf_count_distance_registry)
        self._field_name_to_distance = {}

        field_specs = dictionary_spec.get_field_specs()

        # Compile the map of field names to field specs
        for spec in field_specs:

            field_name = spec.get_name()
            field_distance = \
                self._distance_functions.get_distance_function(spec)

            self._field_name_to_distance[field_name] = field_distance

    def distance(self, obj_a, obj_b):
        """
        :param obj_a: one dictionary
        :param obj_b: another dictionary
        :return: some measure of distance between a and b
        """

        # Get preliminary None checks out of the way
        if obj_a is None and obj_b is None:
            return 0.0

        # Find all the keys we need to look for
        all_keys = self._field_name_to_distance.keys()

        # Technically they are equal if neither has any fields.
        if len(all_keys) == 0:
            return 0.0

        if obj_a is None or obj_b is None:
            n_fields = self._leaf_count_distance.distance(obj_a, obj_b)
            return n_fields

        # From here on out we know a and b are both non-None
        all_values_squared = 0.0
        for key in all_keys:

            # Get the values in the dictionary for the same key
            a_value = obj_a.get(key, None)
            b_value = obj_b.get(key, None)

            # Note that at least one of the dictionaries had to have the
            # key in order for us to get here, so they cannot both be None.

            # At least one of the values didn't exist for the keys
            if a_value is None or b_value is None:
                all_values_squared = all_values_squared + self.NORMALIZED_MAX
                continue

            # From here on out we know the classes are the same of a and b
            # values.  Next be sure we know how to actually judge distance.
            a_value_distance = self._field_name_to_distance.get(key, None)
            if a_value_distance is None:
                # Don't know how judge distance, assume they are far apart
                all_values_squared = all_values_squared + self.NORMALIZED_MAX
                continue

            # There was a bit in the original java to see if the classes
            # of the data could be compared. We are forgoing that here in
            # Python-landia.

            # Now that we know they are equivalent, call the distance function
            field_distance = a_value_distance.distance(a_value, b_value)
            all_values_squared += math.pow(field_distance, self._field_exponent)

        distance = math.pow(all_values_squared, 1.0 / self._field_exponent)
        return distance

    def get_point_class(self):
        return TypeKeywords.DICTIONARY
