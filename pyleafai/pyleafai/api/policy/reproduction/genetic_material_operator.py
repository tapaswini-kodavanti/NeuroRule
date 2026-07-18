
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

class GeneticMaterialOperator():

    """
    This class contains the methods that can be used to create GeneticMaterial
    by any number of parents (including 1 and 0).
    """

    def create_from(self, parents, parent_metrics):
        """
        Creates children from the passed immutable iterable collection of
        parents.  In other words, create new GeneticMaterial instances of the
        same type from the passed ones, if any.

        :param parents: an immutable iterable collection of GeneticMaterial
            that can be used to create new GeneticMaterial.
            Can be an empty collection, but not None.
        :param parent_metrics: an immutable iterable collection of metrics
            associated with each respective parent.
        :return: an iterable collection of children
        """
        raise NotImplementedError
