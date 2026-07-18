
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


from pyleafai.toolkit.policy.math.weights import Weights
from pyleafai.toolkit.policy.serialization.parsers.double_list_parser \
    import DoubleListParser
from pyleafai.toolkit.policy.serialization.parsers.parser import Parser


class WeightsParser(Parser):
    '''
    A utility class that contains an ordered list of doubles
    which represent relative probabilities.
    '''

    def parse(self, input_obj):
        '''
        :param input_obj: a space-delimited string containing a list
                of weights
        :return: the Weights object corresponding to the list of doubles to
                use as weights
        '''

        list_parser = DoubleListParser()
        raw_weights = list_parser.parse_list(input_obj)

        weights = Weights(raw_weights)
        return weights
