
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
from pyleafai.toolkit.data.math.weighted_entity import WeightedEntity


class Weights():
    """
    A utility class that contains an ordered list of
    WeightedEntities (object poinrt + double weight)
    often representing relative probabilities.

    This is *not* a Data-Only class, so it does not really belong
    in data.math.
    """

    def __init__(self, weights):
        """
        Constructor.

        :param weights: a List of doubles, Weightables or WeightedEntities
            to be used as the bases for raw weights in the WeightsOperations
            class.

            Will construct a new list of WeightedEntities given the input.
            So even if you pass in a list of WeightedEntities,
            get_weighted_entities() will return a different list instance.
        """

        use_weights = weights
        if use_weights is None:
            use_weights = []

        new_weighted_entities = []
        for weighty in use_weights:

            # Assume it's a WeightedEntity until proven otherwise
            weighted_entity = weighty
            if not isinstance(weighty, WeightedEntity):

                # Assume its a double to start
                weight = weighty
                entity = None

                # If it's a Weightable, get the weight itself from the interface
                # and the entity is the object itself.
                if isinstance(weighty, Weightable):
                    weight = weighty.get_weight()
                    entity = weighty

                weighted_entity = WeightedEntity(weight, entity)

            new_weighted_entities.append(weighted_entity)

        self._weighted_entities = new_weighted_entities

    def get_weighted_entities(self):
        """
        :return: the list of WeightedEntities that associate weights with
                 the objects
        """
        return self._weighted_entities
