
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


class EvolvedStructureSpec(EvolvedParameterSpec):
    '''
    EvolvedStructureSpec is not GeneticMaterial, per se, but is meta-data about
    just how a particular structure representing GeneticMaterial can be
    evolved.

    Subclasses of self class might add other bits of data for particular
    kinds of data.
    '''

    def __init__(self, name, data_class, field_specs, field_change_rate=1.0):
        '''
        Constructor.

        Creates a new EvolvedParameter meta-data describing some composable
        aspect of Genetic Material.

        :param name: the name for the parameter
        :param data_class: the java class representing/containing the data
                        for the parameter.
        :param field_specs: a list of EvolvedParameterSpecs that describe
                        the evolutionary bounds for each field.
        :param field_change_rate: a probability between 0.0 and 1.0 reflecting
                        how often any given field of the structure changes.
                        By default this is 1.0.
        '''

        super().__init__(name, data_class)

        self._field_specs = field_specs
        self._field_change_rate = field_change_rate

    def get_field_change_rate(self):
        '''
        :return: the field change rate
        '''
        return self._field_change_rate

    def get_field_specs(self):
        '''
        :return: the list of field specs
        '''
        return self._field_specs
