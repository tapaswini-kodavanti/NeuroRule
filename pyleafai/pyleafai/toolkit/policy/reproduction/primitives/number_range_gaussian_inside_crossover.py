
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

import math

from pyleafai.toolkit.policy.reproduction.abstractions.simple_crossover \
    import SimpleCrossover
from pyleafai.toolkit.policy.reproduction.primitives.number_range_gaussian_helper \
    import NumberRangeGaussianHelper


class NumberRangeGaussianInsideCrossover(SimpleCrossover):
    '''
    Creates a Number from two parents by means of finding the midpoint between
    the two parents in a mapped space and using that as a center for a gaussian
    distribution whose standard deviation is the distance between the midpoint
    and either parent.

    Assumes a continuous parameter Range defined by an upper and lower
    bounds (inclusive), and a function along which a linear distribution of
    values can be mapped for appropriate interpretation.

    For instance a mapping function of y = x, crosses over values by finding
    the midpoint along a linear scale.

    A mapping function of y = ln(x) and inverse function of y = log(x) crossed
    over values by a finding the midpoint along a log scale.

    The type of the Number -- int or float -- is determined by the type of
    the values in the given parameter Range.

    This should facilitate binary search.
    '''

    # pylint: disable=too-many-positional-arguments
    def __init__(self, random,
                 evolved_number_spec=None,
                 parameter_range=None,
                 scaling_functions=None,
                 scaled_precision=None):
        '''
        Constructor where all parameters of the Genetic Operator are specified
        via an EvolvedNumber or individually.

        Uses quantization based on the scaled precision and bounds from the
        evolved_number_spec.

        :param random:
                a Random number generator used for making random decisions.
        :param evolved_number_spec:
                an EvolvedNumber object specifying relevant aspects
                of the evolved parameter.
        :param parameter_range:
                a Range object specifying the upper and lower bounds of the
                evolved parameter. This Range is inclusive for non-floating
                point types. Exclusive on the upper bounds for floating point
                types (see Random.next_double()).
        :param scaling_functions:
                a ScalingFunctions object which provides a scaling function
                and its inverse for mapping to non-linear scales
                (like log scales).
        :param scaled_precision:
                  the quantization precision to use when picking numbers within
                  the range.  The default is None.  If no scaled_precision
                  is specified here or in any given EvolvedNumber, then
                  no quantization on created values is performed.
        '''

        self._helper = NumberRangeGaussianHelper(random, evolved_number_spec,
                                                 parameter_range, scaling_functions,
                                                 scaled_precision)

    def crossover(self, mommy, daddy):
        '''
        Fulfill the SimpleCrossover interface.
        :param mommy: 1st basis for crossover
        :param daddy: 2nd basis for crossover
        :return: a new guy based on crossover described.
        '''
        next_gaussian = self._helper.random.next_gaussian()
        return self.crossover_with_decision(mommy, daddy, next_gaussian)

    def crossover_with_decision(self, mommy, daddy, next_gaussian):
        '''
        Perform the operation with any randomness determined outside
        this method.  This makes all the mechanics easier to test.

        :param mommy: one parent which is the basis for crossover
        :param daddy: the other parent which is the basis for crossover
        :param next_gaussian: a random number picked with a gaussian
            distribution
        :return: a single new guy
        '''

        scaling_function = self._helper.scaling_functions.get_scaling_function()
        mapped_mommy_type = scaling_function.apply(mommy)
        mapped_daddy_type = scaling_function.apply(daddy)

        mapped_mommy = float(mapped_mommy_type)
        mapped_daddy = float(mapped_daddy_type)

        #  Find the average of the parents parameters.
        #  Use this as the mean for our gaussian distribution.
        #  Compromise in the family. :)
        mapped_center = (mapped_mommy + mapped_daddy) / 2.0

        #  Find the full span of the range we wish to pick from
        mapped_span = math.fabs(mapped_daddy - mapped_mommy)

        parameter = self._helper.gaussify_with_decision(
                            mapped_center, mapped_span,
                            next_gaussian, mommy)
        return parameter
