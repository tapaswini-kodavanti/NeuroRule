
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


class Deserializer():
    """
    An interface which takes an byte stream and deserializes from its format
    into an object.
    """

    def to_object(self, fileobj):
        """
        :param fileobj: The object to deserialize.
                It is expected that the object be open
                and be pointing at the beginning of the data
                (ala seek to the beginning).

                After calling this method, the seek pointer
                will be at the end of the data. Closing of the
                object is left to the caller.
        :return: the deserialized object
        """
        raise NotImplementedError
