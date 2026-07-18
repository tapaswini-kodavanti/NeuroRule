
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

from pyleafai.toolkit.policy.reproduction.abstractions.operator_suite \
    import OperatorSuite

from pyleafai.toolkit.policy.reproduction.structures.all_fields_structure_crossover \
    import AllFieldsStructureCrossover
from pyleafai.toolkit.policy.reproduction.structures.all_fields_structure_mutator \
    import AllFieldsStructureMutator
from pyleafai.toolkit.policy.reproduction.structures.structure_creator \
    import StructureCreator


class StructureOperatorSuite(OperatorSuite):
    '''
    An OperatorSuite base class which contains a specific, ordered list of
    other OperatorSuites each corresponding to a field in the structure
    to be evolved.

    Note that we use the term "Structure" here as an abstract term of art
    meaning "something that can store values via a field key".  Just how
    that storage is implemented is left abstract at this level.
    Examples of structures to evolve might be a specific class or
    a dictionary Map.
    '''

    def __init__(self, evolved_structure_spec, helper):
        '''
        Subclass Constructor.

        :param evolved_structure_spec:
                an EvolvedStructureSpec object specifying relevant aspects of
                the evolved structure for reproduction.
        :param helper:
                an AbstractStructureOperatorHelper that knows how to
                deal with Structure storage and construction, and which
                has all of the field operator suites registered with it
        '''
        super().__init__(evolved_structure_spec)

        self._helper = helper
        self._suites = helper.get_field_suites()

        self.default_registration()

    #
    #  Getter methods
    #

    def get_suites(self):
        '''
        :return: the suites that comprise the operators for the evolved
               structure's fields.
        '''
        return self._suites

    def get_helper(self):
        '''
        :return: the helper that assists in figuring out class storage
        '''
        return self._helper

    def get_evolved_structure_spec(self):
        '''
        :return: the EvolvedStructureSpec used for this suite instance.
        '''
        return self.get_evolved_parameter_spec()

    def register_field_suite(self, field_suite):
        '''
        This method allows a StructureOperatorSuite to be instantiated
        without having to know all the fields before hand.

        :param fieldSuite: an OperatorSuite to be registered for a field
                in the structure to be evolved
        :return: the instance of the StructureOperatorSuite so that chains
                of these calls might be used in a Builder Pattern
        '''
        self._suites.add(field_suite)
        return self

    def default_registration(self):
        '''
        Do the default registration of GeneticMaterialOperators for
        structures.
        '''

        self.register(StructureCreator(self._helper))

        self.register(AllFieldsStructureMutator(self._helper))

        self.register(AllFieldsStructureCrossover(self._helper))
