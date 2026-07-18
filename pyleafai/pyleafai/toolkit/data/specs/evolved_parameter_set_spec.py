
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


class EvolvedParameterSetSpec(EvolvedParameterSpec):
    '''
    EvolvedParameterSetSpec is not GeneticMaterial, per se, but is meta-data
    about some specific aspect of composable Genetic Material concerning the
    constraints upon a single parameter which is to be evolved amongst a
    specific set of valid values.
    '''

    def __init__(self, name, element_class, object_set):
        '''
        Constructor.

        Creates a new EvolvedParameter meta-data instance describing the
        constraints against which a parameter choosing amongst a set of
        values should be evolved.

        :param name: the name for the parameter
        :param element_class:
                the string representing the class comprising the data
                inside the set
        :param object_set: the set of values to use when picking new values
        '''
        super().__init__(name, element_class)
        self._object_set = set(object_set)

    def get_object_set(self):
        '''
        :return: the Set of values to use
        '''
        return self._object_set
