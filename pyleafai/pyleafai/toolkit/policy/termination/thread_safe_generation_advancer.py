
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

from pyleafai.toolkit.policy.termination.generation_advancer \
    import GenerationAdvancer


class ThreadSafeGenerationAdvancer(GenerationAdvancer):
    '''
    A thread-safe class maintaining the state of the generation count.

    Generally this is injected as a singleton, so generation counting
    can be consistent among all consumers that inject it.

    Note that if your application requires pickling this object
    to restore state, pickle does not like locks.
    '''

    def __init__(self, initial_generation_count=0, generation_count=None):
        '''
        Constructor.

        :param initial_generation_count:
            the initial value for the generation count.
            Default value is 0.
        :param generation_count: the value for the generation count.
            This might be different from initial_generation_count if,
            for example, state of an experiment is being restored from
            something persisted.  Default value is None, implying
            a use of the same value for initial_generation_count.
        '''
        super().__init__(initial_generation_count, generation_count)
        self._lock = threading.Lock()

    def get_generation_count(self):
        '''
        :return: the current generation count
        '''
        count = None
        with self._lock:
            count = super().get_generation_count()
        return count

    def is_initial_generation_count(self):
        '''
        :return: true if the generation count is at its initial value
        '''
        is_initial = None
        with self._lock:
            is_initial = super().is_initial_generation_count()
        return is_initial

    def advance(self):
        '''
        Increments by one the current generation count value.

        Method is not on GenerationCounter interface itself because we intend
        this only to be used by a Terminator, otherwise undefined results will
        occur.
        '''
        with self._lock:
            super().advance()
