
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

from pyleafai.toolkit.policy.math.generation_counter import GenerationCounter
from pyleafai.toolkit.policy.reproduction.uniqueids.integer_unique_identifier_generator \
    import IntegerUniqueIdentifierGenerator


class GenerationScopedUniqueIdentifierGenerator(IntegerUniqueIdentifierGenerator,
                                                GenerationCounter):
    """
    UniqueIdentifierGenerator implementation whose ids are of the form:
    "<generation_id>_<id>".  While the id strings as a whole are still
    unique to the experiment, the split nature means that the secondary <id>
    is unique only to the generation in which it pertains.

    Since we are able to store the generation id here, we also implement
    the GenerationCounter interface to provide pyleaf-y read-only access
    to that.
    """

    def __init__(self, generation_id, initial_id=1):
        '''
        Constructor.

        :param generation_id: The generation id to use when constructing
                    the unique identifier strings of this implementation
        :param initial_id: the initial value for the first call to
                    next_unique_identifier().
        '''
        super().__init__(initial_id=initial_id)
        self._generation_id = str(generation_id)

    def next_unique_identifier(self):
        '''
        :return: the next unique identifier as a string
        '''
        int_id = super().next_unique_identifier()
        unique_id = self.create_id(self._generation_id, int_id)
        return unique_id

    def get_generation_count(self):
        '''
        :return: the current generation count
        '''
        return int(self._generation_id)

    def is_initial_generation_count(self):
        '''
        Warning: With this particular implementation, we don't really
        know if it's the initial generation count or not.

        :return: true if the generation count is at its initial value.
        '''
        return False

    @staticmethod
    def create_id(generation_id, individual_id):
        """
        Generates a unique id for a generation and an individual id
        :param generation_id: the generation id
        :param individual_id: the individual id
        :return: a string
        """
        identifier = f"{generation_id}_{individual_id}"
        return identifier
