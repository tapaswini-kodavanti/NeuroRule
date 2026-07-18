
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

from pyleafai.toolkit.policy.reproduction.uniqueids.unique_identifier_generator \
    import UniqueIdentifierGenerator


class IntegerUniqueIdentifierGenerator(UniqueIdentifierGenerator):
    '''
    A UniqueIdentifierGenerator implementation that uses long integers as the
    basis for identification.
    '''

    def __init__(self, initial_id=1):
        '''
        :param initial_id: the initial value for the first call to
                    next_unique_identifier().
        '''
        self._next_id = initial_id

    def next_unique_identifier(self):
        '''
        :return: the next unique identifier as a string
        '''

        next_id = self._next_id
        self._next_id = self._next_id + 1

        next_id_string = str(next_id)
        return next_id_string
