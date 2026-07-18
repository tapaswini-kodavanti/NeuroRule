
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

from pyleafai.api.policy.reproduction.genetic_material_operator \
    import GeneticMaterialOperator


class IndividualGenerator(GeneticMaterialOperator):
    '''
    This class contains methods that can be used to create Individuals.

    The intention is that the create_from() method here can use a
    composition of various GeneticMaterialGenerators to
    handle the GeneticMaterial.
    '''

    def create_from(self, parents, parent_metrics):
        '''
        Creates children from the passed parents. In other words,
        create new Individual instances from the passed ones, if any.

        :param parents: an immutable collection of Individual that can be
            used to create new Individuals. Can be an empty collection,
            but not None.
        :param parent_metrics: an immutable iterable collection of metrics
            associated with each respective parent.

            This argument is included to adhere to the GeneticMaterialOperator
            spec, but since subclasses are meant to be dealing with Individuals,
            those constructs already have metrics on them and parent_metrics
            will largely be ignored in any implementation.

        :return: a Collection of children
        '''
        return self.create_from_individuals(parents)

    def create_from_individuals(self, parents):
        '''
        Creates children from the passed parents. In other words,
        create new Individual instances from the passed ones, if any.

        :param parents: an immutable collection of Individual that can be
            used to create new Individuals. Can be an empty collection,
            but not None.
        :param parent_metrics: an immutable iterable collection of metrics
            associated with each respective parent.

            Since subclasses are meant to be dealing with Individuals,
            those constructs already have metrics on them and parent_metrics
            will largely be ignored.

        :return: a Collection of children
        '''
        raise NotImplementedError
