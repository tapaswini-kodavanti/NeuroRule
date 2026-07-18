
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

import uuid

from pyleafai.toolkit.policy.reproduction.uniqueids.unique_identifier_generator \
    import UniqueIdentifierGenerator


class UuidUniqueIdentifierGenerator(UniqueIdentifierGenerator):
    '''
    A UniqueIdentifierGenerator implementation that generates
    universally unique identifiers (UUIDs) as the identifier.
    '''

    def next_unique_identifier(self):
        '''
        :return: the next unique identifier as a string
        '''

        new_uuid = uuid.uuid4()
        unique_id = str(new_uuid)
        return unique_id
