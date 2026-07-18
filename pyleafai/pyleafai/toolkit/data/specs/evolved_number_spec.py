
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

from pyleafai.toolkit.data.math.range import Range
from pyleafai.toolkit.data.math.scale_keywords import ScaleKeywords
from pyleafai.toolkit.data.specs.evolved_parameter_spec \
    import EvolvedParameterSpec


class EvolvedNumberSpec(EvolvedParameterSpec):
    '''
    EvolvedNumberSpec is not GeneticMaterial, per se, but is meta-data about
    some specific aspect of composable Genetic Material concerning the
    numeric constraints upon what is to be evolved.
    '''

    # pylint: disable=too-many-positional-arguments
    def __init__(self, name, data_class,
                 unscaled_lower_bound,
                 unscaled_upper_bound,
                 scaled_precision=1.0,
                 scaling_functions=ScaleKeywords.IDENTITY):
        '''
        Constructor.

        Creates a new EvolvedParameterSpec meta-data describing some composable
        aspect of Genetic Material along a potentialy scaled range with a
        defined scaled precision.

        :param name:
                the name for the parameter
        :param data_class:
                the string representing the class comprising the data for the
                parameter
        :param unscaled_lower_bound:
                the lower bound (inclusive) of possible values
        :param unscaled_upper_bound:
                the upper bound of possible values.
                This upperBound is inclusive for non-floating point types.
                Exclusive on the upper bounds for floating point types.
                (see Random.nextDouble()).
        :param scaled_precision:
                the precision of the changes to numeric values in the scaled
                space.
        :param scaling_functions:
                a string name which maps to a ScalingFunctions instance
                providing a scaling function of the form:
                y = scaleFunction.apply(x)
                which transforms a linear distribution of values to something
                else, and its inverse function.
                Default is "identity"
        '''

        super().__init__(name, data_class)
        self._unscaled_parameter_range = Range(unscaled_lower_bound,
                                               unscaled_upper_bound)
        self._scaled_precision = scaled_precision

        self._scaling_functions = scaling_functions

    def get_unscaled_parameter_range(self):
        '''
        :return: the unscaled parameter range for this EvolvedNumberSpec.
        '''
        return self._unscaled_parameter_range

    def get_scaled_precision(self):
        '''
        :return: the precision of jumps for this EvolvedNumberSpec in the
            scaled space.
        '''
        return self._scaled_precision

    def get_scaling_functions(self):
        '''
        :return: the string name for the ScalingFunctions used for
                 this EvolvedNumberSpec.
        '''
        return self._scaling_functions
