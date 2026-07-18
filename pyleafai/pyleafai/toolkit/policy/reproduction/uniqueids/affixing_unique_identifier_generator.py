
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

from pyleafai.toolkit.policy.reproduction.uniqueids.integer_unique_identifier_generator \
    import IntegerUniqueIdentifierGenerator
from pyleafai.toolkit.policy.reproduction.uniqueids.unique_identifier_generator \
    import UniqueIdentifierGenerator


class AffixingUniqueIdentifierGenerator(UniqueIdentifierGenerator):
    '''
    A UniqueIdentifierGenerator implementation that uses another implementation
    to handle the unique id functionality by composition, but allows for
    adding a prefix and/or suffix to the strings with a specified delimiter.
    '''

    def __init__(self, basis_unique_id_generator=None,
                 prefix="", suffix="", delimiter=""):
        '''
        :param basis_unique_id_generator: A UniqueIdentifierGenerator
            that contains the meat of the unique id generation.
            Default is None, implying a simple IntegerUniqueIdentifierGenerator
            will be the default implementation for the basis.
        :param prefix: The prefix to prepend to each unique id string generated
            Default of empty string.
        :param suffix: The suffix to append to each unique id string generated
            Default of empty string.
        :param delimiter: The single delimiter to stick between prefixes
                and suffixes.
            Default of empty string.
        '''

        self._basis = basis_unique_id_generator
        if self._basis is None:
            self._basis = IntegerUniqueIdentifierGenerator()

        self._prefix = prefix
        self._suffix = suffix
        self._delimiter = delimiter

    def next_unique_identifier(self):
        '''
        :return: the next unique identifier as a string
        '''

        basis_id_string = self._basis.next_unique_identifier()
        next_id_string = f"{self._prefix}{self._delimiter}{basis_id_string}"
        next_id_string += f"{self._delimiter}{self._suffix}"
        return next_id_string
