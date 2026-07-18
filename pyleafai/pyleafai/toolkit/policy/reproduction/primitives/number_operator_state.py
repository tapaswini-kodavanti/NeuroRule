
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

from pyleafai.toolkit.policy.math.quantizer import Quantizer
from pyleafai.toolkit.policy.math.scaling_functions_factory \
    import ScalingFunctionsFactory


class NumberOperatorState():
    '''
    State from the common constructor elements of all GeneticMaterialOperators
    dealing with Numbers (doubles or ints).

    This class is the single place where all the policy concerning
    optional constructor arguments is implemented.

    The type of the Number -- int or float -- is determined by the type of
    the values in the given parameter Range.
    '''

    # pylint: disable=too-many-positional-arguments
    def __init__(self, random,
                 evolved_number_spec=None,
                 parameter_range=None,
                 scaling_functions=None,
                 scaled_precision=None):
        '''
        Constructor where all parameters of the Genetic Operator are specified
        via an EvolvedNumberSpec or individually.

        Uses quantization based on the scaled precision and bounds from the
        evolved_number_spec.

        :param random:
                a Random number generator used for making random decisions.
        :param evolved_number_spec:
                an EvolvedNumberSpec object specifying relevant aspects
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
                  is specified here or in any given EvolvedNumberSpec, then
                  no quantization on created values is performed.
        '''
        self.random = random

        self.unmapped_parameter_range = parameter_range
        self.scaling_functions = scaling_functions
        use_scaled_precision = scaled_precision

        # Get information from the EvolvedNumberSpec, if applicable
        if evolved_number_spec is not None:
            self.unmapped_parameter_range = \
                evolved_number_spec.get_unscaled_parameter_range()
            self.scaling_functions = \
                evolved_number_spec.get_scaling_functions()
            use_scaled_precision = evolved_number_spec.get_scaled_precision()

        # Decode a name for the scaling functions, if that is what was given
        if self.scaling_functions is None or \
                isinstance(self.scaling_functions, str):

            factory = ScalingFunctionsFactory()
            self.scaling_functions = factory.create(self.scaling_functions)

        # Set up a Quantizer for use in the main operation
        self.quantizer = None
        if use_scaled_precision is not None:
            self.quantizer = Quantizer.build(self.unmapped_parameter_range,
                                             self.scaling_functions,
                                             use_scaled_precision)
