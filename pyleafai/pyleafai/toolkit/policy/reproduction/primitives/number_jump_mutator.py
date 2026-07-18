
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

from pyleafai.toolkit.policy.reproduction.abstractions.simple_mutator \
    import SimpleMutator
from pyleafai.toolkit.policy.reproduction.primitives.number_operator_state \
    import NumberOperatorState


class NumberJumpMutator(SimpleMutator):
    '''
    Creates a Number from a single parent assuming a continuous
    unmapped parameter Range defined by an upper and lower bounds (inclusive),
    and a function along which a linear distribution of values can be mapped
    for appropriate interpretation.

    For instance a mapping function of y = x, mutates values by a given jump
    along a linear scale.

    A mapping function of y = ln(x) and inverse function of y = log(x)
    mutates values by a given jump along a log scale.

    The type of the Number -- int or float -- is determined by the type of
    the values in the given parameter Range.

    Policy is to increment the existing parameter by a constant in the mapped
    space.
    '''

    # pylint: disable=too-many-positional-arguments
    def __init__(self, random,
                 evolved_number_spec=None,
                 parameter_range=None,
                 scaling_functions=None,
                 scaled_precision=None,
                 mapped_jump_precision=1.0):
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
       :param mapped_jump_precision:
                how far the mutation can leap in the mapped/scaled space.
                Can be positive or negative.
        '''
        self._state = NumberOperatorState(random, evolved_number_spec,
                                          parameter_range, scaling_functions,
                                          scaled_precision)

        self._mapped_jump_precision = mapped_jump_precision

    def mutate(self, basis):
        """
        Fulfills the SimpleMutator superclass interface.

        :param basis: the basis for mutation
        :return: a new instance of a number, based off the original basis
        """
        direction = self._state.random.next_boolean()
        newbie = self.mutate_with_decision(basis, direction)
        return newbie

    def mutate_with_decision(self, basis, direction):
        '''
        Perform the operation with any randomness determined outside
        this method.  This makes all the mechanics easier to test.

        :param basis: the single parent which is the basis for mutation
        :param direction: the direction the jump will take. True is positive.
        :return: a single new guy
        '''

        scaling_function = self._state.scaling_functions.get_scaling_function()

        # Jump by a prescribed amount
        mapped_basis_type = scaling_function.apply(basis)
        mapped_basis = float(mapped_basis_type)

        # Make a random decision as to the sign of the jump.
        sign = 1.0
        if not direction:
            sign = -1.0
        mapped_jump = sign * self._mapped_jump_precision
        mapped_parameter = mapped_basis + mapped_jump

        # Quantizer handles clamping
        mapped_quantized = self._state.quantizer.quantize(mapped_parameter)

        # Do the inverse mapping before storing in a new genetic material
        # instance so the the genetic material can be in its natural units
        caster = DoubleToNumber(basis)
        mapped_parameter_type = caster.cast_to_type(mapped_quantized)

        inverse_function = \
            self._state.scaling_functions.get_inverse_scaling_function()
        parameter = inverse_function.apply(mapped_parameter_type)

        return parameter
