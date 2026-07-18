
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


class DistanceRegistry():

    """
    A helper class for determining a class of Distance function for a
    given class/string data type.

    This is most useful for a branch node of a given representation.
    In this context a "branch node" is one that is a non-primitive container for
    multiple bits of evolvable data, like a structure or a list.
    """

    def __init__(self):
        """
        Constructor.
        """
        self._class_to_distance_map = {}
        self._class_search_order = []
        self.prepare_default_class_maps()

    def prepare_default_class_maps(self):
        """
        Prepare the class maps that dictate class search order
        and which Distance function gets associated with which class.
        Called from the constructor.
        """
        return

    def get_distance_function(self, spec):
        """
        Use the class maps to get the distance function for the given spec.
        Some special cases exist when the Specs have good boundary information.

        :param spec: the EvolvedParameter whose distance function we want
        :return: a Distance function for the given spec
        """

        value_class = spec.get_data_class()
        (value_distance, found_class) = \
            self.find_registered_value_distance(value_class)
        if value_distance is None:
            value_distance = self.special_case_value_distance(found_class, spec)

        return value_distance

    def find_registered_value_distance(self, data_class):
        """
        An initial attempt to find the Distance function given the string
        of the value class.  An implementation may or may not have stored
        a spec-less implementation in the registry, and this method is
        used for finding those.  Called from get_distance_function().

        :param data_class: The String keyword representing the class
            of the value whose distance we want to measure.
        :return: a Distance function implementation, if a spec-less one
            has been registered with the data class type. None otherwise.
        """

        # Look for assignable status
        value_distance = None
        found_class = None

        for class_key in self._class_search_order:
            if class_key == data_class:
                value_distance = self._class_to_distance_map.get(class_key)
                found_class = class_key
                break

        return (value_distance, found_class)

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
        # Note: _ is Pythonic for unused variable
        _ = data_class
        _ = spec
        special_case = None
        return special_case

    def register(self, type_keyword, distance_implementation=None):
        """
        Register the type_keyword.
        If a static implementation for the type without a spec instance is
        available, then the distance_implementation is given on the arg list
        here. Otherwise, the distance_implementation can remain the default
        None, and a sublcass implementation can take care of the extra
        cases in an overridden get_distance_function() method above.
        Order of registration matters for search order.

        :param type_keyword: The String data type to register
        :param distance_implmentation: a static no-spec implmentation.
            By default this is None, indicating that the super class
            will need to pass the spec along in get_distance_function()
            to make the distance measurement meaningful.
        """
        self._class_to_distance_map[type_keyword] = distance_implementation
        self._class_search_order.append(type_keyword)
