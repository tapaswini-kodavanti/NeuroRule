
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

from pyleafai.toolkit.policy.reproduction.abstractions.simple_creator \
    import SimpleCreator


class StructureCreator(SimpleCreator):
    '''
    A class which can create a particular class structure from scratch,
    randomizing each of its fields according to the constraints already given
    to the OperatorSuites which define its fields.
    '''

    def __init__(self, helper):
        '''
        Constructor.

        :param helper:
                an AbstractStructureOperatorHelper that knows how to
                deal with structure storage and construction, and which
                has all of the field operator suites registered with it
        '''

        self._helper = helper
        self._no_parents = []

    def create(self):
        '''
        Fulfill the SimpleCreator interface.
        '''
        # Creators never need metrics from their parents since there are no parents
        parent_metrics = None
        newbie = self._helper.create_one_from_parents(self._no_parents,
                                                      parent_metrics)
        return newbie
