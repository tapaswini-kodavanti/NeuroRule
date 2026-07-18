
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

from pyleafai.toolkit.data.math.type_keywords import TypeKeywords

from pyleafai.api.policy.distance.distance import Distance


class DictionaryLeafCountDistance(Distance):
    """
    A measure of distance between two dictionaries where the entire
    tree of the dictionary is flattened -- this is to say, every leaf
    node is treated with the same weight in the distance calculation.

    Each leaf field which can be optimized counts as an extra unit of
    1.0 towards the total distance calculation.

    Worth noting that this implementation only takes into account keys
    that are specified in the EvolvedStructure spec. If there are extra
    keys, they are not counted at all towards the distance because
    we don't have information enough to know their depth.
    """

    NORMALIZED_MAX = 1.0

    def __init__(self, dictionary_spec, leaf_count_distance_registry):
        """
        Constructor.

        :param dictionary_spec: the EvolvedStrucutre instance
                 representing the spec of the dictionary
        :param leaf_count_distance_registry:
            a DistanceFunctionRegistry for data-class string to
            leaf-node counting Distance function lookup.
        """

        self._distance_functions = leaf_count_distance_registry

        field_specs = dictionary_spec.get_field_specs()

        # Compile the map of field names to field specs
        self._field_name_to_distance = {}
        for spec in field_specs:

            field_name = spec.get_name()
            field_distance = self._distance_functions.get_distance_function(spec)

            self._field_name_to_distance[field_name] = field_distance

    def distance(self, obj_a, obj_b):
        """
        :param obj_a: one dictionary instance
        :param obj_b: another dictionary instance
        :return: the number of leaf nodes to optimize if all fields
                 were flattened
        """

        # Find all the keys
        all_keys = self._field_name_to_distance.keys()

        if len(all_keys) == 0:
            # Technically there is nothing to count
            return 0.0

        num_leaf_nodes = 0.0
        for key, value in self._field_name_to_distance.items():

            # Find the distance function that will count leaves for us
            leaf_count_distance_func = value
            if leaf_count_distance_func is None:
                # Don't know how judge distance, still count it
                num_leaf_nodes = num_leaf_nodes + self.NORMALIZED_MAX
                continue

            # Get the values to pass into the next tier of distance function
            a_value = obj_a.get(key, None)
            b_value = obj_b.get(key, None)

            # See how many leaves there are for the key
            field_distance = leaf_count_distance_func.distance(a_value, b_value)
            num_leaf_nodes = num_leaf_nodes + field_distance

        return num_leaf_nodes

    def get_point_class(self):
        return TypeKeywords.DICTIONARY
