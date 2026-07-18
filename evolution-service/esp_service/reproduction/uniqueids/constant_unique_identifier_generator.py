
# Copyright (C) 2019-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# esp-service Software in commercial settings.
#
# END COPYRIGHT

"""
See class comments for details
"""

from pyleafai.toolkit.policy.reproduction.uniqueids.unique_identifier_generator \
    import UniqueIdentifierGenerator


# pylint: disable=too-few-public-methods
class ConstantUniqueIdentifierGenerator(UniqueIdentifierGenerator):
    """
    UniqueIdentifierGenerator implementation whose ids are always
    the same constant passed in at construct time.

    This is useful for tests.
    """

    def __init__(self, only_id):
        '''
        Constructor.

        :param only_id: The only identifier that will ever come out
                of this implementation
        '''
        self._only_id = only_id

    def next_unique_identifier(self):
        '''
        :return: the next unique identifier as a string
        '''
        return self._only_id
