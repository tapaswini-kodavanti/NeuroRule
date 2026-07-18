
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

from pyleafai.toolkit.policy.serialization.parsers.enum_set_parser \
    import EnumSetParser


class EnumSetParserTest(unittest.TestCase):
    '''
    Tests for EnumSetParser.

    While this guy simply tests the EnumSetParser, that class stands on top
    of a lot of other things which get exercised in the process:
    ListParser, SetParser, and EnumSetParser
    '''

    def __init__(self, args):
        super().__init__(args)

        self._enum_1 = "_enum_1"
        self._enum_2 = "_enum_2"
        self._enum_3 = "_enum_3"
        enum_list = [self._enum_1, self._enum_2, self._enum_3]
        self._enum_set = set(enum_list)

        # Not throwing exceptions on bad member parses just yet
        self._doing_exceptions = True

    def test_assumptions(self):
        '''
        Tests our assumptions about Set behavior independent of the SetParser.
        '''
        size = len(self._enum_set)
        self.assertEqual(3, size)

    def test_parser_create(self):
        '''
        Tests construction of an EnumSetParser.
        '''

        parser = EnumSetParser(self._enum_set)
        self.assertIsNotNone(parser)

    def test_successful_parse_with_commas(self):
        '''
        Tests successful variations of calls of parse_set().
        '''
        parser = EnumSetParser(self._enum_set, delimiter_regex="[,]",
                               raise_on_problems=False)

        # Test one element
        enum_set = parser.parse_set("_enum_2")
        size = len(enum_set)
        self.assertEqual(1, size)

        # Test two elements
        enum_set = parser.parse_set("_enum_1, _enum_3")
        size = len(enum_set)
        self.assertEqual(2, size)

        # Test the contents of the two-element set
        self.assertTrue(self._enum_1 in enum_set)
        self.assertFalse(self._enum_2 in enum_set)
        self.assertTrue(self._enum_3 in enum_set)

        # Test three elements out of order, vary the spacing a bit
        enum_set = parser.parse_set(" _enum_1, _enum_3 ,  \n _enum_2  ")
        size = len(enum_set)
        self.assertEqual(3, size)

        # Test repeated elements with tight commas.
        enum_set = parser.parse_set("_enum_1,ENUM_ONE,ENUM_ONE")
        size = len(enum_set)
        self.assertEqual(1, size)

        # Test no elements
        enum_set = parser.parse_set("")
        size = len(enum_set)
        self.assertEqual(0, size)

        # Test None string
        enum_set = parser.parse_set(None)
        size = len(enum_set)
        self.assertEqual(0, size)

        # Test all empty components
        enum_set = parser.parse_set(" ,   ,")
        size = len(enum_set)
        self.assertEqual(0, size)

    def test_unsuccessful_lower_case_parse(self):
        '''
        Tests unsuccessful variations of calls of parse_set().
        These tests will produce warnings.
        '''
        parser = EnumSetParser(self._enum_set)

        # Test wrong case
        got_excpetion = False
        try:
            enum_set = parser.parse_set("enum_two")
            size = len(enum_set)
            self.assertEqual(0, size)
        # pylint: disable=broad-exception-caught
        except BaseException:
            got_excpetion = True

        self.assertEqual(self._doing_exceptions, got_excpetion)

    def test_unsuccessful_space_case_parse(self):
        '''
        Tests unsuccessful variations of calls of parse_set().
        These tests will produce warnings.
        '''
        parser = EnumSetParser(self._enum_set, delimiter_regex="[ ]")

        # Test space in name
        got_excpetion = False
        try:
            enum_set = parser.parse_set("ENUM 1")
            size = len(enum_set)
            self.assertEqual(0, size)
        # pylint: disable=broad-exception-caught
        except BaseException:
            got_excpetion = True

        self.assertEqual(self._doing_exceptions, got_excpetion)

    def test_successful_parse_with_spaces(self):
        '''
        Tests successful variations of calls of parse_set().
        Since commas make Guice dependency injection difficult with
        Apache Configuration providing the properties, we have turned to
        spaces as delimiters for most cases instead of commas.
        '''
        parser = EnumSetParser(self._enum_set, raise_on_problems=False)

        # Test one element
        enum_set = parser.parse_set("_enum_2")
        size = len(enum_set)
        self.assertEqual(1, size)

        # Test two elements
        enum_set = parser.parse_set("_enum_1 _enum_3")
        size = len(enum_set)
        self.assertEqual(2, size)

        # Test the contents of the two-element set
        self.assertTrue(self._enum_1 in enum_set)
        self.assertFalse(self._enum_2 in enum_set)
        self.assertTrue(self._enum_3 in enum_set)

        # Test three elements out of order, vary the spacing a bit
        enum_set = parser.parse_set(" _enum_1 _enum_3   \n _enum_2  ")
        size = len(enum_set)
        self.assertEqual(3, size)

        # Test repeated elements with tight commas.
        enum_set = parser.parse_set("_enum_1 ENUM_ONE ENUM_ONE")
        size = len(enum_set)
        self.assertEqual(1, size)

        # Test all empty components
        enum_set = parser.parse_set("      ")
        size = len(enum_set)
        self.assertEqual(0, size)
