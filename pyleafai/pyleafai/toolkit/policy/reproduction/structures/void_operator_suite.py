
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
from pyleafai.toolkit.data.specs.evolved_structure_spec \
    import EvolvedStructureSpec

from pyleafai.toolkit.policy.reproduction.structures.dictionary_operator_suite \
    import DictionaryOperatorSuite


class VoidOperatorSuite(DictionaryOperatorSuite):
    '''
    An OperatorSuite which can be used as a placeholder when there is
    no structure to evolve in an abstraction.

    When a VoidOperatorSuite is specified as a member's OperatorSuite
    nested in another StructureOperatorSuite, we assume that there are no
    arguments specified for the member in the higher-level structures'
    class constructor.
    '''

    def __init__(self, name):
        '''
        Constructor.

        :param name: the String name of the field that should *not* be evolved
        '''

        # Note: Java implmentationderived from
        #       ClassStructureOperatorSuite.

        random = None
        no_operator_suites = []

        no_field_specs = []
        evolved_structure = EvolvedStructureSpec(name, TypeKeywords.VOID,
                                                 no_field_specs,
                                                 field_change_rate=0.0)
        super().__init__(random, evolved_structure, no_operator_suites)
