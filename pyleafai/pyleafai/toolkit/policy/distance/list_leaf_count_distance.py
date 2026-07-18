
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

from pyleafai.api.policy.distance.distance import Distance

from pyleafai.toolkit.data.math.type_keywords import TypeKeywords


class ListLeafCountDistance(Distance):
    """
    A measure of distance between two lists where the entire
    sub-tree of the list is flattened -- this is to say, every leaf
    node is treated with the same weight in the distance calculation.

    Each leaf field which can be optimized counts as an extra unit of
    1.0 towards the total distance calculation.
    """

    NORMALIZED_MAX = 1.0

    def __init__(self, list_spec, leaf_count_distance_registry):
        """
        Constructor.

        :param list_spec: the EvolvedListSpec instance
                 representing the spec of the list
        :param leaf_count_distance_registry:
            a DistanceFunctionRegistry for data-class string to
            leaf-node counting Distance function lookup.
        """

        self._distance_functions = leaf_count_distance_registry
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

        # Start with one for the size of the list
        num_leaf_nodes = self.NORMALIZED_MAX

        if self._component_distance_func is None:
            # Don't know how judge distance for any component,
            return num_leaf_nodes

        a_size = 0
        if obj_a is not None:
            a_size = len(obj_a)

        b_size = 0
        if obj_b is not None:
            b_size = len(obj_b)

        max_size = max(a_size, b_size)
        if max_size == 0:
            return num_leaf_nodes

        # Looping through each component helps ensure correct leaf-node
        # assessment for heterogeneous lists.
        for i in range(max_size):

            # Get an appropriate component value for each list
            a_value = None
            if obj_a is not None and i < a_size:
                a_value = obj_a[i]

            b_value = None
            if obj_b is not None and i < b_size:
                b_value = obj_b[i]

            # See how many leaves there are for the component
            component_distance = self._component_distance_func.distance(a_value,
                                                                        b_value)
            num_leaf_nodes += component_distance

        return num_leaf_nodes

    def get_point_class(self):
        return TypeKeywords.LIST
