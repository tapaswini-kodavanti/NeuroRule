
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


class NumberMidpointCrossover(SimpleCrossover):
    '''
    Creates a Number from two parents by means of finding the midpoint between
    the two parents in a mapped space.  Assumes a continuous
    unmapped parameter Range defined by an upper and lower bounds (inclusive),
    and a function along which a linear distribution of values can be mapped
    for appropriate interpretation.

    For instance a mapping function of y = x, crosses over values by finding
    the midpoint along a linear scale.

    The type of the Number -- int or float -- is determined by the type of
    the values in the given parameter Range.

    A mapping function of y = ln(x) and inverse function of y = log(x) crossed
    over values by a finding the midpoint along a log scale.

    This should facilitate binary search.
    '''

    def __init__(self,
                 evolved_number_spec=None,
                 parameter_range=None,
                 scaling_functions=None,
                 scaled_precision=None):
        '''
        Constructor where all parameters of the Genetic Operator are specified
        via an EvolvedNumber or individually.

        Uses quantization based on the scaled precision and bounds from the
        evolved_number_spec.

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

        self._state = NumberOperatorState(None, evolved_number_spec,
                                          parameter_range, scaling_functions,
                                          scaled_precision)

    def crossover(self, mommy, daddy):
        '''
        :param mommy: 1st basis for crossover
        :param daddy: 2nd basis for crossover
        :return: a new guy based on crossover described.
        '''

        scaling_function = self._state.scaling_functions.get_scaling_function()
        mapped_mommy_type = scaling_function.apply(mommy)
        mapped_daddy_type = scaling_function.apply(daddy)

        mapped_mommy = float(mapped_mommy_type)
        mapped_daddy = float(mapped_daddy_type)

        # Find the average of the parents parameters.
        # Compromise in the family. :)
        mapped_parameter = (mapped_mommy + mapped_daddy) / 2.0

        # Quantize if we have a quantizer
        if self._state.quantizer is not None:
            quantized = self._state.quantizer.quantize(mapped_parameter)
            mapped_parameter = quantized

        # Since we are guaranteed both mommy and daddy's parameter are within
        # the acceptable range, we do not have to do any range checks here.

        # Do the inverse mapping before storing in a new genetic material
        # instance so the the genetic material can be in its natural units
        caster = DoubleToNumber(type_example=mommy)
        mapped_parameter_type = caster.cast_to_type(mapped_parameter)

        inverse_function = \
            self._state.scaling_functions.get_inverse_scaling_function()
        parameter = inverse_function.apply(mapped_parameter_type)

        return parameter
