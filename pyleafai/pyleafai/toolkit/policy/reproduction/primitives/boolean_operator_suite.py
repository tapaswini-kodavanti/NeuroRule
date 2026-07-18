
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
from pyleafai.toolkit.policy.reproduction.primitives.boolean_creator \
    import BooleanCreator
from pyleafai.toolkit.policy.reproduction.primitives.boolean_complement_mutator \
    import BooleanComplementMutator
from pyleafai.toolkit.policy.reproduction.primitives.pick_one_crossover \
    import PickOneCrossover


class BooleanOperatorSuite(OperatorSuite):
    '''
    A class which, given an EvolvedParameterSpec specification,
    can put together a suite of GeneticMaterialOperators to
    assist in evolving that Boolean.
    '''

    def __init__(self, random, evolved_boolean_spec):
        '''
        Constructor.

        :param random: a Random number generator used for random decisions
        :param evolved_boolean_spec:
            an EvolvedParameterSpec object specifying relevant aspects of
            the evolved parameter for reproduction.
        '''

        super().__init__(evolved_boolean_spec)
        self.default_registration(random)

    def default_registration(self, random):
        '''
        Do the default registration of GeneticMaterialOperators.

        :param random: Random number generator
        '''

        #  Create and register the Creators we will use.
        self.register(BooleanCreator(random))

        #  Create and register the Mutators we will use.
        self.register(BooleanComplementMutator())

        #  Create and register the Crossovers we will use
        self.register(PickOneCrossover(random))
