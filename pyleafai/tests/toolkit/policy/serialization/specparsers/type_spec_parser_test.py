
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
from pyleafai.toolkit.data.specs.evolved_number_spec \
    import EvolvedNumberSpec
from pyleafai.toolkit.data.specs.evolved_parameter_set_spec \
    import EvolvedParameterSetSpec

from pyleafai.toolkit.policy.serialization.specparsers.type_spec_parser \
    import TypeSpecParser


class TypeSpecParserTest(unittest.TestCase):
    """
    Tests for TypeSpecParser.
    """

    def test_assumptions(self):
        """
        Test our basic assumptions about the class we want to test.
        Often: Can I construct it? but sometimes other tests too.
        """
        parser = TypeSpecParser()
        self.assertIsNotNone(parser)

    def test_double(self):
        """
        Test the ability to parse a spec for a Double
        """

        field_dict_object = {
           "type": "Double",
           "lowerBound": 1e-4,
           "upperBound": 1e-3
        }

        parser = TypeSpecParser()
        spec = parser.parse_spec("learning_rate", None, field_dict_object)

        # Check the type of the spec
        self.assertIsNotNone(spec)
        self.assertIsInstance(spec, EvolvedNumberSpec)

        # Check the range
        spec_range = spec.get_unscaled_parameter_range()
        self.assertIsInstance(spec_range, Range)
        lower = spec_range.get_lower_endpoint()
        upper = spec_range.get_upper_endpoint()
        self.assertEqual(lower, 1e-4)
        self.assertEqual(upper, 1e-3)

    def test_tuple_choice(self):
        """
        Test the ability to parse a spec for a choice of tuples
        """

        field_dict_object = {
            "type": "Tuple",
            "choice": [(2, 2)]
        }

        parser = TypeSpecParser()
        spec = parser.parse_spec("size", None, field_dict_object)

        # Check the type of the spec
        self.assertIsNotNone(spec)
        self.assertIsInstance(spec, EvolvedParameterSetSpec)

        # Check the type of the set spec
        data_class = spec.get_data_class()
        self.assertEqual(data_class, "tuple")

        # Check the set itself
        object_set = spec.get_object_set()
        self.assertEqual(1, len(object_set))
