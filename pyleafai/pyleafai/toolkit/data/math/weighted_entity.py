
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


from pyleafai.toolkit.data.math.weightable import Weightable


class WeightedEntity(Weightable):
    """
    A data-only implementation of Weightable which associates a single
    double weight with some other object.
    """

    def __init__(self, weight, entity=None):
        """
        Constructor.

        :param weight: The single double weight to associate with the entity
        :param entity: The entity to be associated witht he given weight value.
                    By default this is None.
        """
        self._weight = weight
        self._entity = entity

    def get_weight(self):
        """
        :return: the double weight associated with the entity.
        """
        return self._weight

    def get_entity(self):
        """
        :return: the entity associated with the weight.
        """
        return self._entity
