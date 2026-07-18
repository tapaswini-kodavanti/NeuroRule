
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
from pyleafai.toolkit.data.specs.evolved_parameter_set_spec \
    import EvolvedParameterSetSpec

from pyleafai.toolkit.policy.math.python_random import PythonRandom
from pyleafai.toolkit.policy.reproduction.primitives.set_value_creator \
    import SetValueCreator


class SetValueTest(unittest.TestCase):
    '''
    Test a bunch of classes related to choosing one among many.
    '''

    RED = "red"
    ORANGE = "orange"
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"
    INDIGO = "indigo"
    VIOLET = "violet"

    def __init__(self, arg):
        super().__init__(arg)

        self.random = None
        self._color_name = "color"

        self._color = [self.RED, self.ORANGE, self.YELLOW, self.GREEN,
                       self.BLUE, self.INDIGO, self.VIOLET]

        self._num_color_names = len(self._color)
        self._max_tries = 100
        self._seen_some = 25

    def init(self):
        '''
        Initialization to happen before each test.
        '''
        self.random = PythonRandom(0)

    def test_spec_no_set(self):
        '''
        Test that the EvolvedParameterSetSpec works as expected
        when no set is specified.
        '''

        enum_spec = EvolvedParameterSetSpec(self._color_name,
                                            TypeKeywords.STRING,
                                            self._color)

        color_set = enum_spec.get_object_set()
        self.assertEqual(self._num_color_names, len(color_set))

    def test_spec_set(self):
        '''
        Test that the EvolvedParameterSetSpec works as expected
        when a set is specified.
        '''

        enum_set_in = [self.BLUE, self.RED]

        enum_spec = EvolvedParameterSetSpec(self._color_name,
                                            TypeKeywords.STRING,
                                            enum_set_in)

        color_set = enum_spec.get_object_set()

        self.assertEqual(len(enum_set_in), len(color_set))
        self.assertTrue(self.RED in color_set)
        self.assertFalse(self.VIOLET in color_set)

    def test_creator(self):
        '''
        Tests the Creator.
        '''

        self.init()

        # Create the list such that there are only a few self._colors
        # to choose from
        enum_list = [self.BLUE, self.RED]

        creator = SetValueCreator(self.random, enum_list)

        #  Initialize a map which counts how many times we have seen each color
        color_hash = {}
        for color in self._color:
            color_hash[color] = 0

        #  Go through a set number of tries of the creator, seeing how
        #  often we get each color.
        # Note: _ is Pythonic for unused variable
        for _ in range(self._max_tries):

            color = creator.create()
            num_seen = color_hash.get(color)
            num_seen = num_seen + 1
            color_hash[color] = num_seen

        #  Make some assertions about what we should see
        num_seen = color_hash.get(self.BLUE, 0)
        self.assertTrue(num_seen > self._seen_some)

        num_seen = color_hash.get(self.RED, 0)
        self.assertTrue(num_seen > self._seen_some)

        num_seen = color_hash.get(self.GREEN, 0)
        self.assertEqual(0, num_seen)

        num_seen = color_hash.get(self.VIOLET, 0)
        self.assertEqual(0, num_seen)
