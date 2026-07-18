
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

from pyleafai.toolkit.data.math.type_keywords import TypeKeywords

from pyleafai.toolkit.data.specs.evolved_number_spec \
    import EvolvedNumberSpec
from pyleafai.toolkit.data.specs.evolved_parameter_set_spec \
    import EvolvedParameterSetSpec
from pyleafai.toolkit.data.specs.evolved_parameter_spec \
    import EvolvedParameterSpec
from pyleafai.toolkit.data.specs.evolved_structure_spec \
    import EvolvedStructureSpec

from pyleafai.toolkit.policy.distance.normalized_dictionary_distance \
    import NormalizedDictionaryDistance


class NormalizedDictionaryDistanceTest(unittest.TestCase):
    """
    Class which tests the NormalizedDictionaryDistance calculation.
    """

    # Enum for testing purposes.
    COLOR = ["RED", "ORANGE", "YELLOW", "GREEN",
             "BLUE", "INDIGO", "VIOLET"]

    # Field names within the dictionary
    TOP_LEVEL = "top-level"

    INT_UPPER = 100

    # We use the ImmutableMap because it's convenient to statically
    # initialize a Map.
    TARGET = {
        TypeKeywords.DOUBLE: 0.5,
        TypeKeywords.INTEGER: 50,
        TypeKeywords.BOOLEAN: True,
        TypeKeywords.STRING: "GREEN"
    }

    LOW_EXTREME = {
        TypeKeywords.DOUBLE: 0.0,
        TypeKeywords.INTEGER: 0,
        TypeKeywords.BOOLEAN: False,
        TypeKeywords.STRING: "RED"
    }

    # Double = we are halfway to target   0.5
    # Integer = we are halfway to target  0.5
    # Boolean = we are not at the target  1.0
    # Enum = we are not at the target     1.0
    # Total leaf-node score               3.0
    # Normalize over 4 fields total       0.75
    LOW_EXTREME_DISTANCE = 0.75

    HIGH_EXTREME = {
        TypeKeywords.DOUBLE: 1.0,
        TypeKeywords.INTEGER: 100,
        TypeKeywords.BOOLEAN: True,
        TypeKeywords.STRING: "VIOLET"
    }

    # Double = we are halfway to target   0.5
    # Integer = we are halfway to target  0.5
    # Boolean = we are at the target      0.0
    # Enum = we are not at the target     1.0
    # Total leaf-node score               2.0
    # Normalize over 4 fields total       0.5
    HIGH_EXTREME_DISTANCE = 0.5

    def __init__(self, *args):
        super().__init__(*args)
        self.distance = None

    def setUp(self):
        """
        Test setup.
        Creates the dictionary schema.
        """

        field_specs = []
        double_field = EvolvedNumberSpec(TypeKeywords.DOUBLE,
                                         TypeKeywords.DOUBLE,
                                         0.0, 1.0)
        field_specs.append(double_field)

        int_field = EvolvedNumberSpec(TypeKeywords.INTEGER,
                                      TypeKeywords.INTEGER,
                                      0, self.INT_UPPER)
        field_specs.append(int_field)

        boolean_field = EvolvedParameterSpec(TypeKeywords.BOOLEAN,
                                             TypeKeywords.BOOLEAN)
        field_specs.append(boolean_field)

        enum_field = EvolvedParameterSetSpec(TypeKeywords.STRING,
                                             TypeKeywords.STRING,
                                             self.COLOR)
        field_specs.append(enum_field)

        dictionary_spec = EvolvedStructureSpec(self.TOP_LEVEL,
                                               TypeKeywords.DICTIONARY, field_specs)

        self.distance = NormalizedDictionaryDistance(dictionary_spec)

    def test_extremes(self):
        """
        Test the extremes of a basic map.
        """

        # Distance to this should always be 0.0
        dist = self.distance.distance(self.TARGET, self.TARGET)
        self.assertEqual(0.0, dist)

        dist = self.distance.distance(self.LOW_EXTREME, self.TARGET)
        self.assertEqual(self.LOW_EXTREME_DISTANCE, dist)

        dist = self.distance.distance(self.HIGH_EXTREME, self.TARGET)
        self.assertEqual(self.HIGH_EXTREME_DISTANCE, dist)
