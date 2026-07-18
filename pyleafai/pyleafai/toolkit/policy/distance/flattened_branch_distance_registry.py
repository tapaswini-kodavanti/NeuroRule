
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

from pyleafai.toolkit.data.specs.evolved_number_spec \
    import EvolvedNumberSpec

from pyleafai.toolkit.policy.distance.all_or_nothing_distance \
    import AllOrNothingDistance
from pyleafai.toolkit.policy.distance.distance_registry import DistanceRegistry
from pyleafai.toolkit.policy.distance.constant_distance import ConstantDistance
from pyleafai.toolkit.policy.distance.flattened_dictionary_distance \
    import FlattenedDictionaryDistance
from pyleafai.toolkit.policy.distance.flattened_list_distance \
    import FlattenedListDistance
from pyleafai.toolkit.policy.distance.normalized_number_distance \
    import NormalizedNumberDistance


class FlattenedBranchDistanceRegistry(DistanceRegistry):
    """
    A DistanceRegistry implementation for determining the correct
    Distance function for a given data class, where the functions are
    a measure of distance between two fields where the entire sub-tree
    is flattened -- this is to say, every leaf node is treated with the
    same weight in the distance calculation.

    In this context a "branch node" is one that is a non-primitive container for
    multiple bits of evolvable data, like a structure or a list
    """

    NORMALIZED_MAX = ConstantDistance.DEFAULT_DISTANCE

    def __init__(self, leaf_count_distance_registry):
        """
        Constructor.

        :param leaf_count_distance_registry: An instantiation of
            LeafCountDistanceRegistry.
        """
        super().__init__()
        self._leaf_count_distance_registry = leaf_count_distance_registry

    def prepare_default_class_maps(self):
        """
        Prepare the class maps that dictate class search order
        and which Distance function gets associated with which class.
        Called from the constructor.
        """

        self._constant_distance = AllOrNothingDistance(self.NORMALIZED_MAX)

        self.register(TypeKeywords.DICTIONARY, None)
        self.register(TypeKeywords.LIST, None)
        self.register(TypeKeywords.DOUBLE, None)
        self.register(TypeKeywords.FLOAT, None)
        self.register(TypeKeywords.INT, None)
        self.register(TypeKeywords.INTEGER, None)
        self.register(TypeKeywords.BOOLEAN, self._constant_distance)
        self.register(TypeKeywords.STRING, self._constant_distance)

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

            structure_spec = spec
            value_distance = FlattenedDictionaryDistance(structure_spec, self,
                                                         self._leaf_count_distance_registry)

        elif TypeKeywords.LIST == data_class:

            # Field is a List
            # Use its spec to create a distance function especially for that
            # list structure with its specific fields.
            list_spec = spec
            value_distance = FlattenedListDistance(list_spec, self,
                                                   self._leaf_count_distance_registry)

        elif data_class in (TypeKeywords.DOUBLE, TypeKeywords.FLOAT,
                            TypeKeywords.INT, TypeKeywords.INTEGER):

            # Field is a Number.
            # Use its spec to create a distance function especially for that
            # Number with its specific Range.
            if isinstance(spec, EvolvedNumberSpec):
                number_spec = spec
                value_distance = NormalizedNumberDistance(number_spec)
            else:
                value_distance = self._constant_distance

        return value_distance
