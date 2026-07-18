
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

from pyleafai.toolkit.data.math.range import Range


class Quantizer():
    '''
    A class which, given a range and a precision, will quantize a given
    value within the range and according to intervals established by the
    precision.

    Other utilities that are useful to preserving the properties of
    certain random distributions are provided here as well, like
    reflect() and clamp().

    XXX Caveats:
        There are some shortcomings of the current implementation in that
        the lower bound of the range is used as the basis for quantization
        intervals and that can sometimes lead to odd side intervals towards
        the upper bound under particular circumstances.

        For instance, consider a range of 0.0 to 1.0 and a precision of 0.3.
        Valid values that can come out of the quantize() method will be:
            0.0, 0.3, 0.6, 0.9, 1.0
    '''

    def __init__(self, quantization_range, precision):
        '''
        Constructor.

        :param quantization_range: the range applicable to the quantization
            XXX range here is a range object with a specific interface.
        :param precision: the precision applicable to the quantization
        '''
        self._range = quantization_range
        self._precision = precision

    def get_range(self):
        '''
        :return: the range applicable to the quantization
        '''
        return self._range

    def get_precision(self):
        '''
        :return: the precision applicable to the quantization
        '''
        return self._precision

    def quantize(self, to_quantize):
        '''
        Quantizes and clamps a value.

        :param to_quantize: a double to quantize given self class's
                range and precision.
        :return: a quantized double
        '''

        #  You might ask: "Why clamp before we call quantize_unclamped()?"
        #  This has to do with edge conditions at the upper bounds,
        #  best explored by a concrete example...
        #
        #  Consider a range from 0.0 to 10.0, with a precision of 3.0,
        #  and an incoming value of 10.1.
        #
        #  The precision presents some quantization weirdness
        #  in that 0.0, 3.0, 6.0, 9.0 and 10.0 are all valid quantized
        #  values, given the algorithm.
        #  This incoming value is clearly past the upper bound of the range.
        #
        #  Without a first round of clamping, the 10.1 value would have
        #  a choice of quantizing to 9.0 or 12.0 (given the precision of
        #  3.0).  Because of the algorithm employed, 9.0 is closer than
        #  12.0, so the value would quantize to 9.0.  Yet because of the
        #  odd arrangement of the precision with the range, the more
        #  explicable value to return would be the upper bound of the
        #  range -- 10.0.
        #
        #  As a result, we do a pre-clamping computation here, and if
        #  the clamped value is different, we know we do not need to
        #  quantize with confusing results.
        #
        #  We check equality with the upper endpoint only because these
        #  quantization artifacts only happen at that end of the range,
        #  as quantization is calibrated from the lower endpoint.
        clamped = self.clamp(to_quantize)
        if clamped != to_quantize or \
                clamped == self._range.get_upper_endpoint():

            #  No need for quantization, we already clamped
            return clamped

        quantized = self.quantize_unclamped(to_quantize)

        #  The value coming back from quantize_unclamped might
        #  be beyond the range due to artifacts of the quantization
        #  process. Clamp again before returning to guarantee something
        #  within the acceptable range.
        clamped = self.clamp(quantized)

        return clamped

    def reflect_and_quantize(self, to_quantize):
        '''
        Reflects and quantizes a value.

        :param to_quantize: a double to quantize given self class's
                range and precision.
        :return: a quantized double
        '''

        reflected = self.reflect(to_quantize)

        quantized = self.quantize_unclamped(reflected)

        #  The value coming back from quantize_unclamped might
        #  be beyond the range due to artifacts of the quantization
        #  process. Clamp again before returning to guarantee something
        #  within the acceptable range.
        clamped = self.clamp(quantized)

        return clamped

    def clamp(self, to_clamp):
        '''
        Clamps a value.

        :param to_clamp: a double to clamp given self class's range.
        :return: a double clamped to the boundaries of the range
        '''

        #  Clamp to lower bound if necessary
        lower_bound = self._range.get_lower_endpoint()
        if to_clamp <= lower_bound:
            return lower_bound

        #  Clamp to upper bound if necessary
        upper_bound = self._range.get_upper_endpoint()
        if to_clamp >= upper_bound:
            return upper_bound

        #  No clamping necessary
        return to_clamp

    def quantize_unclamped(self, to_quantize):
        '''
        Quantizes a value.

        :param to_quantize a double to quantize given self class's
                range and precision.
        :return: a quantized double
        '''

        #  See if value is already quantized
        lower_bound = self._range.get_lower_endpoint()
        distance_to_lower_bound = to_quantize - lower_bound
        num_quanta = distance_to_lower_bound / self._precision
        floor_quanta = math.floor(num_quanta)

        #  See if we were dead on with the floor_quanta.
        #  If so, just use that to finish out the rest.
        #  If not, there is more to do.
        floor_quanta_distance = num_quanta - floor_quanta
        use_quanta = floor_quanta
        if floor_quanta_distance != 0.0:

            #  See which is closer -- the floor or the ceiling
            #  At self point, floor is always less than num_quanta
            #  and ceiling is always greater than num_quanta.
            ceiling_quanta = math.ceil(num_quanta)
            ceiling_quanta_distance = ceiling_quanta - num_quanta
            use_quanta = ceiling_quanta
            if floor_quanta_distance <= ceiling_quanta_distance:
                use_quanta = floor_quanta

        #  Convert use_quanta back to something within range
        quantized_distance_to_lower_bound = use_quanta * self._precision
        quantized = lower_bound + quantized_distance_to_lower_bound

        return quantized

    def reflect(self, to_reflect):
        '''
        Reflects a value back once from the appropriate endpoint of the range.
        Note that it is conceivable that multiple reflections might need to
        take place to guarantee a value lies within a specific range, but
        self method only handles a single iteration of that.

        :param to_reflect: a double to reflect given self class's range.
        :return: a double reflected off the boundaries of the range,
                if such reflection is appropriate.
        '''

        #  Reflect off lower bound if necessary
        lower_bound = self._range.get_lower_endpoint()
        if to_reflect <= lower_bound:
            #  Find the distance to_reflect has overshot the lower_bound
            distance = lower_bound - to_reflect

            #  Now use that distance to reflect back towards the center of range
            reflection = lower_bound + distance
            return reflection

        #  Reflect off upper bound if necessary
        upper_bound = self._range.get_upper_endpoint()
        if to_reflect >= upper_bound:
            #  Find the distance to_reflect has overshot the upper_bound
            distance = to_reflect - upper_bound

            #  Now use that distance to reflect back towards the center of range
            reflection = upper_bound - distance
            return reflection

        #  No reflection necessary
        return to_reflect

    @classmethod
    def build(cls, unscaled_range, scaling_functions, scaled_precision):
        '''
        Builds a Quantizer

        :param unscaled_range:
                a Range object specifying the upper and lower bounds of the
                quantization.
        :param scaling_functions:
                a ScalingFunctions object which provides a scaling function
                and its inverse for mapping to non-linear scales
                (like log scales).
        :param scaled_precision:
                the quantization precision to use when picking numbers within
                the range.
        :return:  a Quantizer set up with the appropriate scaled Range and
                precision
        '''

        typed_lower_bound = unscaled_range.get_lower_endpoint()
        typed_upper_bound = unscaled_range.get_upper_endpoint()

        #  Find the end points in terms of the given function
        scaling_function = scaling_functions.get_scaling_function()
        scaled_lower = scaling_function.apply(typed_lower_bound)
        scaled_upper = scaling_function.apply(typed_upper_bound)

        # Expecting double range here
        my_range = Range(float(scaled_lower), float(scaled_upper))

        quantizer = Quantizer(my_range, scaled_precision)
        return quantizer
