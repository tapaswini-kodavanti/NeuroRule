
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

from pyleafai.toolkit.policy.reproduction.abstractions.simple_mutator \
    import SimpleMutator
from pyleafai.toolkit.policy.reproduction.primitives.number_range_gaussian_helper \
    import NumberRangeGaussianHelper


class NumberRangeGaussianMutator(SimpleMutator):
    '''
    Creates a Number from a single parent assuming a continuous
    parameter Range defined by an upper and lower bounds (inclusive),
    and a function along which a linear distribution of values can be mapped
    for appropriate interpretation.

    Policy is to choose an offset from a gaussian/normal distribution
    whose basis for the standard deviation is equal to half the full
    range / span of the parameter to be evolved multiplied by a constant factor.

    For instance a mapping function of y = x, mutates values by a given jump
    along a linear scale.

    A mapping function of y = ln(x) and inverse function of y = log(x) mutates
    values by a given jump along a log scale.

    The type of the Number -- int or float -- is determined by the type of
    the values in the given parameter Range.

    After choosing the the new point along the appropriate scale, the value
    is quantized along the same scale.
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

        #  Find out the scale factor for how far we can jump.
        mapped_range = self._helper.get_mapped_range()
        self._mapped_span = mapped_range.get_upper_endpoint() - \
            mapped_range.get_lower_endpoint()

    def mutate(self, basis):
        '''
        Fulfill the SimpleMutator interface.

        :param basis: basis for mutation.
        :return: a new guy based on mutation
        '''
        next_gaussian = self._helper.random.next_gaussian()
        return self.mutate_with_decision(basis, next_gaussian)

    def mutate_with_decision(self, basis, next_gaussian):
        '''
        Perform the operation with any randomness determined outside
        this method.  This makes all the mechanics easier to test.

        :param basis: the single parent which is the basis for mutation
        :param next_gaussian: a random number picked with a gaussian
                    distribution
        :return: a single new guy
        '''

        scaling_function = self._helper.scaling_functions.get_scaling_function()

        # Find out starting point from the basis
        mapped_basis_type = scaling_function.apply(basis)
        mapped_basis = float(mapped_basis_type)

        parameter = self._helper.gaussify_with_decision(
                            mapped_basis, self._mapped_span,
                            next_gaussian, basis)
        return parameter
