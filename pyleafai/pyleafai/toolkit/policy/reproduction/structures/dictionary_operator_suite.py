
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

from pyleafai.toolkit.policy.reproduction.structures.dictionary_structure_operator_helper \
    import DictionaryStructureOperatorHelper
from pyleafai.toolkit.policy.reproduction.structures.structure_operator_suite \
    import StructureOperatorSuite


class DictionaryOperatorSuite(StructureOperatorSuite):
    '''
    An OperatorSuite which contains Operators needed for a dictionary
    object to be evolved.
    '''

    def __init__(self, random, evolved_structure_spec, op_suites):
        '''
        Constructor.

        :param random:
                  random number generator for random decisions
        :param evolved_structure_spec:
                an EvolvedStructureSpec object specifying relevant aspects of
                the evolved structure for reproduction.
        :param op_suites:
                a map of field OperatorSuites, where each entry corresponds to
                the suite to be used for a particular field in the structure
                to evolve.
        '''

        helper = DictionaryStructureOperatorHelper(
                        random,
                        evolved_structure_spec, op_suites,
                        evolved_structure_spec.get_field_change_rate())

        super().__init__(evolved_structure_spec, helper)
