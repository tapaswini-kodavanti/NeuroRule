
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

from pyleafai.toolkit.policy.serialization.parsers.list_parser \
    import ListParser


class SetParser(ListParser):
    '''
    Class which can parse a set of the values from
    a list in a single String, returning a Set as the result.

    The bigger idea here is that an instance of this class can be used to
    parse a String value of a property and use the resulting Set from
    the parse_set() method as a value in some parameter.

    This class works as-is with parsing set of Strings, but subclasses
    can provide specific type_type parsers to get specific type values
    back from each set-element string passed in there.

    The delimiter to use for the list can be specified in the constructor.
    '''

    def parse(self, input_obj):
        '''
        Fulfills the Parser interface

        :param input_obj: the string to parse
        :return: an object parsed from that string
        '''
        return self.parse_set(input_obj)

    def parse_set(self, input_string):
        '''
        :param input_string: a String representing a delimiter-separated list of
               values

        :return: an Set containing the parsed values found
            in the delimiter-separated list provided by the input_string.
            Warnings will be issued when a component of the list cannot be
            parsed.
        '''

        value_list = super().parse_list(input_string)

        # Defer to the implementation to make a Set out of the value List.
        new_set = self.create_set(value_list)
        return new_set

    def create_set(self, value_list):
        '''
        A default implementation that knows how to create a
        set from a give list of values.

        Subclasses might override this, as some classes have specific
        Set typing associated with them (like Enums).

        XXX This method is really provided more for porting compatibility
        with the Java.

        :param value_list: the full List of valid values
        :return: a Set of valid values.
        '''
        new_set = set(value_list)
        return new_set
