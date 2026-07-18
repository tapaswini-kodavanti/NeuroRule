
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
from pyleafai.toolkit.policy.reproduction.primitives.set_value_creator \
    import SetValueCreator
from pyleafai.toolkit.policy.reproduction.primitives.set_value_mutator \
    import SetValueMutator
from pyleafai.toolkit.policy.reproduction.primitives.pick_one_crossover \
    import PickOneCrossover


class SetValueOperatorSuite(OperatorSuite):
    '''
    A class which, given an EvolvedParameterSetSpec specification,
    can put together a suite of GeneticMaterialOperators to
    assist in evolving from a set of specific values for the Type.
    '''

    def __init__(self, random, evolved_parameter_set_spec):
        '''
        Constructor.

        :param random: a Random number generator used for random decisions
        :param evolved_parameter_set_spec:
            an EvolvedParameterSetSpec object specifying relevant aspects of
            the evolved parameter for reproduction.
        '''

        super().__init__(evolved_parameter_set_spec)
        self.default_registration(random)

    def default_registration(self, random):
        '''
        Do the default registration of GeneticMaterialOperators.

        :param random: random number generator
        '''

        evolved_parameter_set_spec = self.get_evolved_parameter_spec()
        the_set = evolved_parameter_set_spec.get_object_set()

        #  Create and register the Creators we will use.
        self.register(SetValueCreator(random, the_set))

        #  Create and register the Mutators we will use.
        self.register(SetValueMutator(random, the_set))

        #  Create and register the Crossovers we will use
        self.register(PickOneCrossover(random))
