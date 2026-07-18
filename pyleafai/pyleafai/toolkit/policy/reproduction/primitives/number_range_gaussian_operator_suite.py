
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
from pyleafai.toolkit.policy.reproduction.primitives.number_creator \
    import NumberCreator
from pyleafai.toolkit.policy.reproduction.primitives.number_range_gaussian_mutator \
    import NumberRangeGaussianMutator
from pyleafai.toolkit.policy.reproduction.primitives.number_range_gaussian_inside_crossover \
    import NumberRangeGaussianInsideCrossover
from pyleafai.toolkit.policy.reproduction.primitives.number_range_gaussian_outside_crossover \
    import NumberRangeGaussianOutsideCrossover


class NumberRangeGaussianOperatorSuite(OperatorSuite):
    '''
    A class which, given an EvolvedNumberSpec specification,
    can put together a suite of GeneticMaterialOperators to
    assist in evolving that Number.

    While the creator operator here picks from a uniform distribution,
    the mutation and crossover operators all use gaussian distributions
    when picking random numbers for their guts.
    '''

    def __init__(self, random, evolved_number_spec):
        '''
        Constructor.

        :param random: a Random number generator used for random decisions
        :param evolved_number_spec:
            an EvolvedNumberSpec object specifying relevant aspects of
            the evolved parameter for reproduction.
        '''

        super().__init__(evolved_number_spec)
        self.default_registration(random)

    def default_registration(self, random):
        '''
        Do the default registration of GeneticMaterialOperators.

        :param random: random number generator
        '''

        evolved_number_spec = self.get_evolved_number_spec()

        #  Create and register the Creators we will use.
        self.register(NumberCreator(random, evolved_number_spec))

        #  Create and register the Mutators we will use.
        #  Note that with only Mutators and no Crossovers, we should
        #  random-walk towards a solution in ~O(N) generations time,
        #  where N is the width of the range of solutions.
        self.register(NumberRangeGaussianMutator(random, evolved_number_spec))

        #  Create and register the Crossovers we will use
        #  Note that with only Crossovers and no Mutators, we should
        #  binary-search towards a solution in ~O(log(N)) generations time,
        #  where N is the width of the range of solutions.
        self.register(NumberRangeGaussianInsideCrossover(
                            random, evolved_number_spec))
        self.register(NumberRangeGaussianOutsideCrossover(
                            random, evolved_number_spec))

    def get_evolved_number_spec(self):
        '''
        :return: the EvolvedNumberSpec used for this suite instance.
        '''
        return self.get_evolved_parameter_spec()
