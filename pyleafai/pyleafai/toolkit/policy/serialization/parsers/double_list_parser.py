
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


from pyleafai.toolkit.policy.serialization.parsers.double_parser \
    import DoubleParser
from pyleafai.toolkit.policy.serialization.parsers.list_parser \
    import ListParser


class DoubleListParser(ListParser):
    '''
    Class which can parse a list of double values from
    a list in a single String, returning a List as the result.

    The bigger idea here is that an instance of this class can be used to
    parse a String value of a property and use the resulting List from
    the parse_list() method as a value in some other data class.

    The delimiter regular expression to use for the list can be specified
    in the constructor.
    '''

    def __init__(self, delimiter_regex=None):
        '''
        Constructor.

        :param delimiter_regex: the delimiter_regex used to separate
                string names of values in a parsed string.
                By default the delimiters are commas *and* spaces.
        '''

        super().__init__(delimiter_regex, DoubleParser())
