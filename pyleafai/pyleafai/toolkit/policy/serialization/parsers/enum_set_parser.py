
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

from pyleafai.toolkit.policy.serialization.parsers.enum_parser \
    import EnumParser
from pyleafai.toolkit.policy.serialization.parsers.set_parser \
    import SetParser


class EnumSetParser(SetParser):
    '''
    Class which can parse a set of enum values from
    a list in a single String, returning a Set as the result.

    The bigger idea here is that an instance of this class can be used to
    parse a String value of a property and use the resulting Set from
    the parse_set() method as a value in some parameter.

    This class works as-is with parsing sets of Strings, but subclasses
    can provide specific type_type parsers to get specific type values
    back from each set-element string passed in there.

    The delimiter to use for the list can be specified in the constructor.
    '''

    def __init__(self, enum_set, delimiter_regex=None,
                 raise_on_problems=True):
        '''
        Constructor.

        :param enum_set: the set consisting of the valid parseable
            enumerated values
        :param delimiter_regex: the delimiter_regex used to separate
                string names of values in a parsed string.
                By default the delimiters are commas *and* spaces.
        :param raise_on_problems: If True (the default), when strings
            are parsed that do not match the enum_set, a ValueError
            will be raised.  If this is False, a value error will
            not be raised, but a message will still be printed
            and a None value will be returned from parse().
        '''
        type_parser = EnumParser(enum_set, raise_on_problems)
        super().__init__(delimiter_regex, type_parser)
