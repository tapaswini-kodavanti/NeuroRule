
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

from pyleafai.toolkit.policy.distance.constant_distance import ConstantDistance
from pyleafai.toolkit.policy.distance.dictionary_leaf_count_distance \
    import DictionaryLeafCountDistance
from pyleafai.toolkit.policy.distance.distance_registry import DistanceRegistry
from pyleafai.toolkit.policy.distance.list_leaf_count_distance \
    import ListLeafCountDistance


class LeafCountDistanceRegistry(DistanceRegistry):
    """
    A DistanceRegistry implementation for determining the correct
    Distance function for a given data class that measures the number
    of leaves on an entire sub-tree of a branch.

    In this context a "branch node" is one that is a non-primitive container for
    multiple bits of evolvable data, like a structure or a list
    """

    NORMALIZED_MAX = ConstantDistance.DEFAULT_DISTANCE

    def prepare_default_class_maps(self):
        """
        Prepare the class maps that dictate class search order
        and which Distance function gets associated with which class.
        Called from the constructor.
        """

        constant_distance = ConstantDistance(self.NORMALIZED_MAX)

        self.register(TypeKeywords.DICTIONARY, None)
        self.register(TypeKeywords.LIST, None)
        self.register(TypeKeywords.DOUBLE, constant_distance)
        self.register(TypeKeywords.FLOAT, constant_distance)
        self.register(TypeKeywords.INTEGER, constant_distance)
        self.register(TypeKeywords.INT, constant_distance)
        self.register(TypeKeywords.BOOLEAN, constant_distance)
        self.register(TypeKeywords.STRING, constant_distance)

    def special_case_value_distance(self, data_class, spec):
        """
        An opportunity for a subclass to provide implementations
        of Distance functions for a data_class where those implementations
        require some knowledge of the spec in order to calculate distance.
        This is applicable for most complex data types.

        :param data_class: The String keyword representing the class
            of the value whose distance we want to measure.
        :param spec: the EvolvedParameter whose distance function we want
        :return: a Distance function implementation, if a spec-less one
            has been registered with the data class type. None otherwise.
        """
        value_distance = None

        # Check for some special cases
        if TypeKeywords.DICTIONARY == data_class:

            # Field is a Dictionary.
            # Use its spec to create a distance function especially for that
            # dictionary structure with its specific fields.

            # EvolvedStructure<Map<String, Object>>
            structure_spec = spec
            value_distance = DictionaryLeafCountDistance(structure_spec, self)

        elif TypeKeywords.LIST == data_class:

            # Field is a List
            # Use its spec to create a distance function especially for that
            # list structure with its specific fields.
            list_spec = spec
            value_distance = ListLeafCountDistance(list_spec, self)

        return value_distance
