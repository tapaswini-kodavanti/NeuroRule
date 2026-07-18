
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

from pyleafai.toolkit.data.specs.evolved_parameter_spec \
    import EvolvedParameterSpec


class EvolvedListSpec(EvolvedParameterSpec):
    '''
    Data-only instance describing the information needed to evolve
    the contents of an ordered List/Array of homogeneous elements/components.
    '''

    # pylint: disable=too-many-positional-arguments
    def __init__(self, name, data_class, component_spec,
                 min_length, max_length, component_change_rate):
        '''
        Constructor.

        :param name: the name of the field we are evolving.
        :param data_class: the storage Class of the List we are evolving
        :param component_spec: an EvolvedParameterSpec which describes the
                evolutionary boundaries for any given component of the list.
        :param min_length: the minimum length of the list to be evolved.
        :param max_length: the maximum length of the list to be evolved.
        :param component_change_rate: the probability (0.0 - 1.0) that any
                given component will change when undergoing a mutation
                or crossover operation
        '''

        super().__init__(name, data_class)
        self._component_spec = component_spec
        self._min_length = min_length
        self._max_length = max_length
        self._component_change_rate = component_change_rate

    def get_component_spec(self):
        '''
        :return: the EvolvedParameterSpec which describes the evolutionary
                boundaries for any given component of the List.
        '''
        return self._component_spec

    def get_min_length(self):
        '''
        :return: the minimum length of the list.
        '''
        return self._min_length

    def get_max_length(self):
        '''
        :return: the maximum length of the list.
        '''
        return self._max_length

    def get_component_change_rate(self):
        '''
        :return: the component change rate of the list
        '''
        return self._component_change_rate
