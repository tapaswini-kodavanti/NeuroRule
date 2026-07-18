
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

from pyleafai.toolkit.policy.math.double_to_number import DoubleToNumber

from pyleafai.toolkit.policy.reproduction.abstractions.simple_creator \
    import SimpleCreator
from pyleafai.toolkit.policy.reproduction.primitives.number_operator_state \
    import NumberOperatorState


class NumberCreator(SimpleCreator):
    '''
    Creates a Number from scratch given a continuous unmapped_parameter_range
    defined by an upper and lower bounds (inclusive), and a function along
    which a linear distribution of values can be mapped for appropriate
    interpretation.

    For instance a mapping function of y = x, picks values along a linear scale.

    A mapping function of y = ln(x) and inverse function of y = log(x) picks
    values along a log scale.

    The type of the Number -- int or float -- is determined by the type of
    the values in the given parameter Range.

    When picking a number along whichever scale, the distribution along that
    scale is uniform.
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
        self._state = NumberOperatorState(random, evolved_number_spec,
                                          parameter_range, scaling_functions,
                                          scaled_precision)

    def create(self):
        '''
        :return: a single new guy.
        '''
        next_double = self._state.random.next_double()
        return self.create_with_decision(next_double)

    def create_with_decision(self, next_double):
        '''
        Perform the operation with any randomness determined outside
        this method.  This makes all the mechanics easier to test.

        :param next_double: a uniform random number between 0.0 and 1.0.
        :return: a single new guy
        '''

        # Find the end points in terms of the given function
        scaling_function = self._state.scaling_functions.get_scaling_function()

        upper_endpoint = self._state.unmapped_parameter_range.get_upper_endpoint()
        lower_endpoint = self._state.unmapped_parameter_range.get_lower_endpoint()

        upper = scaling_function.apply(upper_endpoint)
        lower = scaling_function.apply(lower_endpoint)

        # Pick a random within the given Range.
        # Do all the arithmetic as doubles before converting back to the Type.
        range_size = float(upper) - float(lower)

        # Use the caster to see if the type we are dealing with is a
        # non-floating point type.  If so, we want the upper bounds
        # of the given range to be included in what can be picked.
        # Consequently, we add 1 to the range size.
        # If the +1 is not added, then the last value of the inclusive
        # floating point range is never picked.
        caster = DoubleToNumber(type_example=lower_endpoint)
        if not caster.is_instance(TypeKeywords.DOUBLE) and \
                not caster.is_instance(TypeKeywords.FLOAT):

            range_size += 1.0

        # Use the random decision that was made externally
        bounded = next_double * range_size
        translated = bounded + float(lower)

        if self._state.quantizer is not None:
            quantized = self._state.quantizer.quantize(translated)
            translated = quantized

        translated_type = caster.cast_to_type(translated)

        #  Use the inverse_function to map back to the scale /
        #  unmapped_parameter_range specified.
        #  This allows the values of Double genetic material to be
        #  used directly, even though the scaling is different.
        inverse_function = \
            self._state.scaling_functions.get_inverse_scaling_function()
        mapped = inverse_function.apply(translated_type)

        return mapped
