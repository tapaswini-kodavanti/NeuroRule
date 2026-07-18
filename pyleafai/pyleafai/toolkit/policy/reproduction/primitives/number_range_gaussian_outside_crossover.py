
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


class NumberRangeGaussianOutsideCrossover(SimpleCrossover):
    '''
    Creates a Number from two parents by choosing a new point between one of
    them and its closer boundary of the range.

    The new point is chosen using a gaussian distribution centered around the
    midpoint of the chosen parent and boundary and whose standard deviation
    is half the span between the two.

    This should facilitate binary search in that it should shake up a population
    which is too bunched up around a single value to look further from its
    radius, but will not have the trappings of picking too many values at the
    edges like the NumberOvershootCrossover does.

    All of this happens in a coordinate space (mapping) of the client code's
    choosing.

    The type of the Number -- int or float -- is determined by the type of
    the values in the given parameter Range.

    Assumes a continuous parameter Range defined by an upper and lower
    bounds (inclusive), and a function along which a linear distribution of
    values can be mapped for appropriate interpretation.

    After choosing a new value in this mapped coordinate space, the new value
    is also quantized within that mapped space before applying the inverse
    of the mapping/scaling function.
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
        :param mommy: 1st parent for crossover
        :param daddy: 2nd parent for crossover
        :return: a new guy based on crossover described.
        '''
        next_gaussian = self._helper.random.next_gaussian()
        choose_mommy = self._helper.random.next_boolean()
        return self.crossover_with_decision(mommy, daddy,
                                            next_gaussian, choose_mommy)

    def crossover_with_decision(self, mommy, daddy,
                                next_gaussian, choose_mommy):

        '''
        Perform the operation with any randomness determined outside
        this method.  This makes all the mechanics easier to test.

        :param mommy: one parent which is the basis for crossover
        :param daddy: the other parent which is the basis for crossover
        :param next_gaussian: a random number picked with a gaussian
                distribution
        :param choose_mommy: a random decision for which basis (mommy or daddy)
                we will use to get closer to the boundary.
        :return: a single new guy
        '''

        # Find the mapped values of mommy and daddy
        scaling_function = self._helper.scaling_functions.get_scaling_function()
        mapped_mommy_typed = scaling_function.apply(mommy)
        mapped_daddy_typed = scaling_function.apply(daddy)

        mapped_mommy = float(mapped_mommy_typed)
        mapped_daddy = float(mapped_daddy_typed)

        # Find the boundaries of the parameter
        lower_bound = self._helper.get_mapped_range().get_lower_endpoint()
        upper_bound = self._helper.get_mapped_range().get_upper_endpoint()

        # See which boundary is closer for each candidate
        mommy_boundary = None
        daddy_boundary = None
        if mapped_mommy > mapped_daddy:
            # mommy is closer to the upper bound
            # daddy is closer to the lower bound
            mommy_boundary = upper_bound
            daddy_boundary = lower_bound
        else:
            # mommy is closer to the lower bound
            # daddy is closer to the upper bound
            mommy_boundary = lower_bound
            daddy_boundary = upper_bound

        # Find how close each candidate is to their boundary
        mommy_to_boundary = math.fabs(mapped_mommy - mommy_boundary)
        daddy_to_boundary = math.fabs(mapped_daddy - daddy_boundary)

        # Pick the two points which will comprise the span we
        # wish to pick between.
        point_a = None
        point_b = None
        if mommy_to_boundary == 0.0 and daddy_to_boundary == 0.0:
            # Both are on their boundaries.
            # There is no way further outward given the pair.
            # Choose amongst the entire parameter span.
            point_a = upper_bound
            point_b = lower_bound
        elif daddy_to_boundary == 0.0 or choose_mommy:
            # Only daddy is on the boundary or
            # No one is on their boundary and we just choose mommy.
            # Choose the span between mommy and her boundary
            point_a = mommy_boundary
            point_b = mapped_mommy
        else:
            # Only mommy is on the boundary or
            # No one is on their boundary and we just choose daddy.
            # Choose the span between daddy and his boundary.
            point_a = daddy_boundary
            point_b = mapped_daddy

        # Figure out the midpoint of the span
        # and the length of half of the span
        mapped_midpoint = (point_a + point_b) / 2.0
        mapped_span = math.fabs(point_a - point_b)

        parameter = self._helper.gaussify_with_decision(
                                mapped_midpoint, mapped_span,
                                next_gaussian, mommy)
        return parameter
