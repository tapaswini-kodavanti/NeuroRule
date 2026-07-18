
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


from pyleafai.toolkit.policy.reproduction.abstractions.simple_operator \
    import SimpleOperator


class SimpleCrossover(SimpleOperator):
    '''
    An abstract convenience class which knows how to mate or "crossover"
    two parents, yielding one and only one instance of GeneticMaterial.
    This class handles the (rather abstract) GeneticMaterialOperator class
    appropriately.

    Subclasses override the crossover() method to create new child versions
    of their GeneticMaterial.

    SimpleCrossover implementations always ignore any parent_metrics coming
    in from the more abstract create_from() method.
    '''

    def crossover(self, mommy, daddy):
        '''
        An easier method for dealing with crossover yielding a single instance
        of a particular GeneticMaterial.

        :param mommy: 1st GeneticMaterial which is to be used as the basis
                for crossing.
        :param daddy: 2nd GeneticMaterial which is to be used as the basis
                for crossing.
        :return: a new instance of the GeneticMaterial based on the two parents
        '''
        raise NotImplementedError

    def create_from(self, parents, parent_metrics):
        '''
        Crosses exactly 2 instances of GeneticMaterial from the passed parents.
        Parents must contain at least 2 instances. If it contains more,
        only 2 will be used and the others will be ignored.

        See SimpleOperator.create_from()
        '''

        n_parents = len(parents)
        if n_parents < self.get_min_parents():
            raise ValueError("Passed more parents than is necessary")

        mommy = parents[0]
        daddy = parents[1]
        newbie = self.crossover(mommy, daddy)
        newbies = [newbie]
        return newbies

    def get_min_parents(self):
        '''
        :return: 2 Always. By definition a Crossover takes 2 parents.
        '''
        return 2
