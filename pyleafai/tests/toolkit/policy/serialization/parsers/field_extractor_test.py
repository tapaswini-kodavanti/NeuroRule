
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

from pyleafai.toolkit.policy.serialization.parsers.field_extractor \
    import FieldExtractor


class FieldExtractorTest(unittest.TestCase):
    """
    Tests the FieldExtractor.
    """

    def setUp(self):
        """
        Method called before each test.
        """
        self.extractor = FieldExtractor()

    def test_simple(self):
        """
        Test getting fields from a flat dictionary
        """

        mydict = {
            "foo": 1.0
        }

        # Test value that exists
        value = self.extractor.get_field(mydict, "foo", 0.0)
        self.assertEqual(value, 1.0)

        # Test value that does not exist
        value = self.extractor.get_field(mydict, "bar", 0.0)
        self.assertEqual(value, 0.0)

    def test_not_dict(self):
        """
        Makes sure the default value comes back when not dealing
        with a dictionary.
        """

        mydict = None
        value = self.extractor.get_field(mydict, "bar", 10.0)
        self.assertEqual(value, 10.0)

        mydict = 1.0
        value = self.extractor.get_field(mydict, "bar", 10.0)
        self.assertEqual(value, 10.0)

    def test_not_string(self):
        """
        Makes sure the right value comes back when dealing
        with a key that is not a string.
        """
        mydict = {
            "foo": 1.0,
            -2.0: 2.0
        }

        # Does default value come back?
        key = -1.0
        value = self.extractor.get_field(mydict, key, 10.0)
        self.assertEqual(value, 10.0)

        # Can we use non-string as key?
        key = -2.0
        value = self.extractor.get_field(mydict, key, 10.0)
        self.assertEqual(value, 2.0)

    def test_nested_dict(self):
        """
        Makes sure the right value comes back when dealing
        with a key implying lookup in nested dictionaries.
        """
        mydict = {
            "foo": 1.0,
            "fitness": {
                "metrics": {
                    "names": "fitness, alt_objective",
                    "maximize": "true, true"
                }
            }
        }

        # Can we use delimited key?
        key = "fitness.metrics.names"
        value = self.extractor.get_field(mydict, key, 0.0)
        self.assertEqual(value, "fitness, alt_objective")

        # Can we use a delimited key that doesn't exist?
        key = "fitness.metrics.goober"
        value = self.extractor.get_field(mydict, key, 0.0)
        self.assertEqual(value, 0.0)

        # Can we use a partially delimited key?
        key = "fitness.metrics"
        value = self.extractor.get_field(mydict, key, 0.0)
        self.assertTrue(isinstance(value, dict))
