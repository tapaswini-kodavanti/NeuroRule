
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


class EvolvedParameterSpec():
    '''
    EvolvedParameterSpec is not GeneticMaterial, per se, but is meta-data
    about some specific aspect of composable Genetic Material concerning
    the constraints upon what is to be evolved.

    Subclasses of self class might add other bits of data for certain kinds
    of data. For instance, Genetic Material surrounding some numeric type
    might involve extra fields pertaining to the range of acceptable values.
    '''

    def __init__(self, name, data_class):
        '''
        Constructor.
        Creates a new EvolvedParameterSpec meta-data describing some composable
        aspect of Genetic Material.

        :param name: the field name for the parameter.  Think of this as
                the key, if data were stored in a dictionary.
        :param data_class: the class name representing/containing the data
                        for the parameter.
        '''
        self._name = name
        self._data_class = data_class

    def get_name(self):
        '''
        :return: the name for self EvolvedParameter.
        '''
        return self._name

    def get_data_class(self):
        '''
        :return: the class representing/containing the data
                        for the parameter.
        '''
        return self._data_class

    def __eq__(self, obj):
        '''
        :param obj: the object to compare to
        :return: the class representing/containing the data
                        for the parameter.
        '''

        if self == obj:
            return True

        if obj is None:
            return False

        same = self.get_name() == obj.get_name()
        same = same and self.get_data_class() == obj.get_data_class()

        return same
