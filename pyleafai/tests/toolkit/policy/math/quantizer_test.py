
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

import unittest

from pyleafai.toolkit.data.math.range import Range
from pyleafai.toolkit.policy.math.quantizer import Quantizer


class QuantizerTest(unittest.TestCase):
    '''
    Tests the Quantizer class.
    '''

    def test_quantize_to_integer(self):
        '''
        Tests quantization on integer boundaries.
        '''

        lower_bound = 0.0
        upper_bound = 100.0
        precision = 1.0
        my_range = Range(lower_bound, upper_bound)

        quantizer = Quantizer(my_range, precision)

        below_range = -1.5
        quantized = quantizer.quantize(below_range)
        self.assertEqual(lower_bound, quantized)

        above_range = 101.5
        quantized = quantizer.quantize(above_range)
        self.assertEqual(upper_bound, quantized)

        at_lower = lower_bound
        quantized = quantizer.quantize(at_lower)
        self.assertEqual(lower_bound, quantized)

        at_upper = upper_bound
        quantized = quantizer.quantize(at_upper)
        self.assertEqual(upper_bound, quantized)

        already_quantized = 10.0
        quantized = quantizer.quantize(already_quantized)
        self.assertEqual(already_quantized, quantized)

        just_above = 10.1
        quantized = quantizer.quantize(just_above)
        self.assertEqual(already_quantized, quantized)

        just_below = 9.9
        quantized = quantizer.quantize(just_below)
        self.assertEqual(already_quantized, quantized)

        at_midpoint = 10.5
        quantized = quantizer.quantize(at_midpoint)
        self.assertEqual(already_quantized, quantized)

    def test_quantize_to_decimal(self):
        '''
        Tests quantization on decimal boundaries.
        '''

        lower_bound = 0.0
        upper_bound = 100.0
        precision = 0.01
        my_range = Range(lower_bound, upper_bound)

        quantizer = Quantizer(my_range, precision)

        below_range = -1.5
        quantized = quantizer.quantize(below_range)
        self.assertEqual(lower_bound, quantized)

        above_range = 101.5
        quantized = quantizer.quantize(above_range)
        self.assertEqual(upper_bound, quantized)

        at_lower = lower_bound
        quantized = quantizer.quantize(at_lower)
        self.assertEqual(lower_bound, quantized)

        at_upper = upper_bound
        quantized = quantizer.quantize(at_upper)
        self.assertEqual(upper_bound, quantized)

        already_quantized = 10.05
        quantized = quantizer.quantize(already_quantized)
        self.assertEqual(already_quantized, quantized)

        just_above = 10.051
        quantized = quantizer.quantize(just_above)
        self.assertEqual(already_quantized, quantized)

        just_below = 10.049
        quantized = quantizer.quantize(just_below)
        self.assertEqual(already_quantized, quantized)

        at_midpoint = 10.055
        quantized = quantizer.quantize(at_midpoint)
        self.assertEqual(already_quantized, quantized)

    def test_quantize_to_odd_integer(self):
        '''
        Tests quantization on odd integer boundaries.
        '''

        lower_bound = 0.0
        upper_bound = 100.0
        precision = 5.0
        my_range = Range(lower_bound, upper_bound)

        quantizer = Quantizer(my_range, precision)

        below_range = -1.5
        quantized = quantizer.quantize(below_range)
        self.assertEqual(lower_bound, quantized)

        above_range = 101.5
        quantized = quantizer.quantize(above_range)
        self.assertEqual(upper_bound, quantized)

        at_lower = lower_bound
        quantized = quantizer.quantize(at_lower)
        self.assertEqual(lower_bound, quantized)

        at_upper = upper_bound
        quantized = quantizer.quantize(at_upper)
        self.assertEqual(upper_bound, quantized)

        already_quantized = 10.0
        quantized = quantizer.quantize(already_quantized)
        self.assertEqual(already_quantized, quantized)

        just_above = 12.1
        quantized = quantizer.quantize(just_above)
        self.assertEqual(already_quantized, quantized)

        just_below = 8.9
        quantized = quantizer.quantize(just_below)
        self.assertEqual(already_quantized, quantized)

        at_midpoint = 12.5
        quantized = quantizer.quantize(at_midpoint)
        self.assertEqual(already_quantized, quantized)

    def test_quantize_to_big_range(self):
        '''
        Tests quantization on integer boundaries when the precision
        exceeds the my_range.
        '''

        lower_bound = 0.0
        upper_bound = 100.0
        precision = 101.0
        my_range = Range(lower_bound, upper_bound)

        quantizer = Quantizer(my_range, precision)

        below_range = -1.5
        quantized = quantizer.quantize(below_range)
        self.assertEqual(lower_bound, quantized)

        above_range = 101.5
        quantized = quantizer.quantize(above_range)
        self.assertEqual(upper_bound, quantized)

        at_lower = lower_bound
        quantized = quantizer.quantize(at_lower)
        self.assertEqual(lower_bound, quantized)

        at_upper = upper_bound
        quantized = quantizer.quantize(at_upper)
        self.assertEqual(upper_bound, quantized)

        just_above_precision_mid = 50.6
        quantized = quantizer.quantize(just_above_precision_mid)
        self.assertEqual(upper_bound, quantized)

        just_below_precision_mid = 50.4
        quantized = quantizer.quantize(just_below_precision_mid)
        self.assertEqual(lower_bound, quantized)

        at_midpoint = 50.5
        quantized = quantizer.quantize(at_midpoint)
        self.assertEqual(lower_bound, quantized)
