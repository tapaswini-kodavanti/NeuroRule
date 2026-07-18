
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

from pyleafai.toolkit.policy.math.double_to_number import DoubleToNumber
from pyleafai.toolkit.policy.reproduction.primitives.number_operator_state \
    import NumberOperatorState


class NumberRangeGaussianHelper(NumberOperatorState):
    '''
    Helper class to consolidate some common logic used amongst the
    NumberRangeGaussian operators.

    The type of the Number -- int or float -- is determined by the type of
    the values in the given parameter Range.
    '''

    # Multiplier for getting a gaussian/normal distribution to fall mostly
    # within a particular range.
    #
    # At 1.0, ~68% of random numbers fall within the range.
    # At 2.0, ~95% of random numbers fall within the range.
    # At 3.0, ~99% of random numbers fall within the range.
    DEFAULT_STANDARD_DEVIATIONS_PER_HALF_SPAN = 3.0

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

        super().__init__(random, evolved_number_spec, parameter_range,
                         scaling_functions, scaled_precision)

        #  XXX  Concievably this could be another tunable parameter,
        #       but we don't have to go there yet.
        self._standard_deviations_per_half_span = \
            self.DEFAULT_STANDARD_DEVIATIONS_PER_HALF_SPAN

    def get_mapped_range(self):
        '''
        :return: the full mapped parameter Range
        '''
        return self.quantizer.get_range()

    def gaussify_with_decision(self, mapped_mean, mapped_span, next_gaussian,
                               class_basis):
        '''
        :param mapped_mean: the center of the gaussian distribution
                    in mapped coordinate space.
        :param mapped_span: the span (distance) in the mapped coordinate
                    space that the gaussian distribution will cover
        :param next_gaussian: a pre-picked double value from
                    Random.next_gaussian(). Passing in this value aids
                    greatly in testing.
        :param class_basis: an instance of the type whose class we will
                    get for conversion purposes from the internal
                    calculations done with doubles.
        :return: an instance of the Type whose value is centered
                around the mapped_mean and whose gaussian distribution
                extends to the span. Before being returned, the value
                is potentially reflected back from the full-range endpoints
                and quantized.
        '''

        # Get half the size of the span
        mapped_half_span = mapped_span / 2.0

        # Figure out how far to jump based on:
        #      a) the gaussian random number
        #      b) the span of the range we want to pick within
        #      c) the scale factor which says how many std deviations
        #         we want within the span.
        mapped_gaussian_scale = mapped_half_span / self._standard_deviations_per_half_span
        mapped_jump = next_gaussian * mapped_gaussian_scale

        # Make the leap!
        mapped_parameter = mapped_mean + mapped_jump

        # Quantize the results.
        # Since we do not want to over-pick results at the range boundary,
        # we use the reflection capability of the quantizer to mirror
        # the normal distribution back towards the center when it reaches
        # an endpoint.
        mapped_quantized = self.quantizer.reflect_and_quantize(mapped_parameter)

        # Do the inverse mapping before storing in a new genetic material
        # instance so the the genetic material can be in its natural units
        caster = DoubleToNumber(type_example=class_basis)
        mapped_parameter_type = caster.cast_to_type(mapped_quantized)

        inverse_function = self.scaling_functions.get_inverse_scaling_function()
        parameter = inverse_function.apply(mapped_parameter_type)

        return parameter
