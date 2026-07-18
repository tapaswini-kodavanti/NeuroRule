
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

from pyleafai.toolkit.data.math.type_keywords import TypeKeywords

from pyleafai.api.policy.distance.distance import Distance

from pyleafai.toolkit.policy.distance.list_leaf_count_distance \
    import ListLeafCountDistance


class FlattenedListDistance(Distance):
    """
    A measure of distance between two lists where the entire
    tree of the list is flattened -- this is to say, every leaf
    node is treated with the same weight in the distance calculation.

    All leaf field distances on components are expected to be normalized to
    values between 0.0 and 1.0.
    """

    def __init__(self, list_spec, flattened_branch_distance_registry,
                 leaf_count_distance_registry,
                 field_exponent=1.0):
        """
        Constructor.

        :param list_spec: the EvolvedListSpec instance
                 representing the spec of the list
        :param flattened_branch_distance_registry: An instantiation of
            FlattenedBranchDistanceRegistry.
        :param leaf_count_distance_registry: An instantiation of
            LeafCountDistanceRegistry.
        :param field_exponent: the exponent used in the distance function
            Default field_exponent is 1.0.

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
        self._leaf_count_distance = ListLeafCountDistance(list_spec,
                                                          leaf_count_distance_registry)
        self._list_spec = list_spec

        component_spec = list_spec.get_component_spec()
        self._component_distance_func = \
            self._distance_functions.get_distance_function(component_spec)

    def distance(self, obj_a, obj_b):
        """
        :param obj_a: one List instance - ignored
        :param obj_b: another List instance - ignored
        :return: the number of leaf nodes to optimize if all components
                 were flattened
        """

        # Get preliminary None checks out of the way
        if obj_a is None and obj_b is None:
            return 0.0

        a_size = 0
        if obj_a is not None:
            a_size = len(obj_a)

        b_size = 0
        if obj_b is not None:
            b_size = len(obj_b)

        max_size = max(a_size, b_size)
        if max_size == 0:
            return 0.0

        if obj_a is None or obj_b is None:
            n_fields = self._leaf_count_distance.distance(obj_a, obj_b)
            return n_fields

        # From here on out we know a and b are both non-None

        #
        # Calculate the size component
        #

        scale = self._list_spec.get_max_length() - self._list_spec.get_min_length()
        # Do not divide by zero
        if scale == 0.0:
            scale = 1.0

        size_diff = math.fabs(a_size - b_size)
        normalized_size_diff = size_diff / scale

        all_values_squared = math.pow(normalized_size_diff,
                                      self._field_exponent)

        # Looping through each component helps ensure correct leaf-node
        # assessment for heterogeneous lists.
        for i in range(max_size):

            # Get an appropriate component value for each list
            a_value = None
            if i < a_size:
                a_value = obj_a[i]

            b_value = None
            if i < b_size:
                b_value = obj_b[i]

            component_distance = self._component_distance_func.distance(a_value,
                                                                        b_value)
            all_values_squared += math.pow(component_distance,
                                           self._field_exponent)

        return all_values_squared

    def get_point_class(self):
        return TypeKeywords.LIST
