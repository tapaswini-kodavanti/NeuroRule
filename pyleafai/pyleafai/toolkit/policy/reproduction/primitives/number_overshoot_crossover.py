
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

from pyleafai.toolkit.policy.reproduction.abstractions.simple_crossover \
    import SimpleCrossover
from pyleafai.toolkit.policy.reproduction.primitives.number_operator_state \
    import NumberOperatorState


class NumberOvershootCrossover(SimpleCrossover):
    '''
    Creates a Number from two parents. Policy is to find the distance between
    the parents and overshoot one of them by the distance already existing
    between them, all in a coordinate space (mapping) of the client code's
    choosing.

    Assumes a continuous unmapped parameter Range defined by an upper and lower
    bounds (inclusive), and a function along which a linear distribution of
    values can be mapped for appropriate interpretation.

    For instance a mapping function of y = x, crosses over values by finding
    the midpoint along a linear scale.

    A mapping function of y = ln(x) and inverse function of y = log(x) crossed
    over values by a finding the midpoint along a log scale.

    The type of the Number -- int or float -- is determined by the type of
    the values in the given parameter Range.

    This should facilitate binary search in that it should shake up a
    population which is too bunched up around a single value to look further
    from its radius.
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

    def crossover(self, mommy, daddy):
        '''
        Fulfills the SimpleCrossover interface
        :param mommy: 1st parent for crossover
        :param daddy: 2nd parent for crossover
        :return: a new guy based on crossover described.
        '''
        # Pick a random integer to determine which direction we will
        # choose -- do we go past the high guy or low guy?
        direction = self._state.random.next_boolean()
        return self.crossover_with_decision(mommy, daddy, direction)

    def crossover_with_decision(self, mommy, daddy, direction):
        '''
        Perform the operation with any randomness determined outside
        this method.  This makes all the mechanics easier to test.

        :param mommy: one parent which is the basis for crossover
        :param daddy: the other parent which is the basis for crossover
        :param direction: the direction the jump will take. True is positive.
        :return: a single new guy
        '''

        scaling_function = self._state.scaling_functions.get_scaling_function()
        mapped_mommy_typed = scaling_function.apply(mommy)
        mapped_daddy_typed = scaling_function.apply(daddy)

        mapped_mommy = float(mapped_mommy_typed)
        mapped_daddy = float(mapped_daddy_typed)

        # Find whose mapped parameter is greater.
        mapped_high = mapped_mommy
        mapped_low = mapped_daddy
        if mapped_daddy > mapped_mommy:
            mapped_high = mapped_daddy
            mapped_low = mapped_mommy

        # Find out the distance between the two.
        # We have confidence this will be a non-negative number.
        mapped_distance = mapped_high - mapped_low

        # Create a new parameter based on the direction.
        # Bound this to the given unmapped parameter Range.
        mapped_parameter = None
        overshoot_high = True
        if direction == overshoot_high:

            mapped_upper_typed = scaling_function.apply(
                self._state.unmapped_parameter_range.get_upper_endpoint())
            mapped_upper = float(mapped_upper_typed)

            # Overshoot in the high direction.
            mapped_parameter = mapped_high + mapped_distance

            # Bound to the unmapped parameter Range
            mapped_parameter = min(mapped_parameter, mapped_upper)

        else:
            mapped_lower_typed = scaling_function.apply(
                    self._state.unmapped_parameter_range.get_lower_endpoint())
            mapped_lower = float(mapped_lower_typed)

            # Overshoot in the low direction.
            mapped_parameter = mapped_low - mapped_distance

            # Bound to the unmapped parameter Range
            mapped_parameter = max(mapped_parameter, mapped_lower)

        if self._state.quantizer is not None:
            mapped_quantized = self._state.quantizer.quantize(mapped_parameter)
            mapped_parameter = mapped_quantized

        # Do the inverse mapping before storing in a new genetic material
        # instance so the the genetic material can be in its natural units
        caster = DoubleToNumber(type_example=mommy)
        mapped_parameter_typed = caster.cast_to_type(mapped_parameter)

        inverse_function = \
            self._state.scaling_functions.get_inverse_scaling_function()
        parameter = inverse_function.apply(mapped_parameter_typed)

        return parameter
