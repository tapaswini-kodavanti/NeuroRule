
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

from pyleafai.toolkit.policy.serialization.parsers.parser import Parser


class EnumParser(Parser):
    '''
    Parser implementation getting a strign enum from an object.
    '''

    def __init__(self, enum_set, raise_on_problems=True):
        '''
        Constructor.

        :param enum_set: The set of strings that must be an exact match
                in order to parse correctly
        :param raise_on_problems: If True (the default), when strings
            are parsed that do not match the enum_set, a ValueError
            will be raised.  If this is False, a value error will
            not be raised, but a message will still be printed
            and a None value will be returned from parse().
        '''
        self._enum_set = enum_set
        self._raise_on_problems = raise_on_problems

    def parse(self, input_obj):
        '''
        :param input_obj: the object to parse

        :return: a string enum parsed from that input object
            if the string is in the given enum set. None otherwise.
        '''
        use_string = str(input_obj)
        if use_string in self._enum_set:
            return use_string

        message = f"{use_string} is not in the set {str(self._enum_set)}"
        if self._raise_on_problems:
            raise ValueError(message)

        print(message)

        return None
