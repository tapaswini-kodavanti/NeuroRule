
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


class DataSourceProvider:
    """
    An interface providing a data Source in the form of Source of Record.
    """

    def get_source(self):
        """
        Provides a data source in the form of Source of Record.

        :return: a Source of Record
        """
        raise NotImplementedError
