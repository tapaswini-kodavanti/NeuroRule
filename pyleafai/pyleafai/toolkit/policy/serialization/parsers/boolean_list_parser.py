
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

from pyleafai.toolkit.policy.serialization.parsers.boolean_parser \
    import BooleanParser
from pyleafai.toolkit.policy.serialization.parsers.list_parser \
    import ListParser


class BooleanListParser(ListParser):
    '''
    A ListParser implementation that parses lists of boolean values
    from a string.
    '''

    def __init__(self, delimiter_regex=None):
        '''
        Constructor

        :param delimiter_regex: the delimiter_regex used to separate
                string names of values in a parsed string.
                By default the delimiters are commas *and* spaces.
        '''
        super().__init__(delimiter_regex, BooleanParser())
