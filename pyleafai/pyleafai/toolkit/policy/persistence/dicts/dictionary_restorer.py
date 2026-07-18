
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

from pyleafai.api.policy.persistence.restorer import Restorer


class DictionaryRestorer(Restorer):
    """
    This interface provides a way to retrieve a dictionary
    from some storage like a file, a database or S3.
    """

    def restore(self):
        """
        :return: a dictionary from some persisted store
        """
        raise NotImplementedError
