
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

import threading

from pyleafai.toolkit.policy.reproduction.uniqueids.integer_unique_identifier_generator \
    import IntegerUniqueIdentifierGenerator
from pyleafai.toolkit.policy.reproduction.uniqueids.unique_identifier_generator \
    import UniqueIdentifierGenerator


class ThreadSafeUniqueIdentifierGenerator(UniqueIdentifierGenerator):
    '''
    A thread-safe wrapper of a basis UniqueIdentifierGenerator.

    Worth noting that if you are considering persisting this class via
    pickle, the implementation contains locks, and pickle does not like locks.
    '''

    def __init__(self, basis_unique_id_generator=None):
        '''
        :param basis_unique_id_generator: A UniqueIdentifierGenerator
            that contains the meat of the unique id generation.
            Default is None, implying a simple IntegerUniqueIdentifierGenerator
            will be the default implementation for the basis.
        '''
        self._lock = threading.Lock()

        self._basis = basis_unique_id_generator
        if self._basis is None:
            self._basis = IntegerUniqueIdentifierGenerator()

    def next_unique_identifier(self):
        '''
        :return: the next unique identifier as a string
        '''

        next_id_string = None
        with self._lock:
            next_id_string = self._basis.next_unique_identifier()
        return next_id_string
