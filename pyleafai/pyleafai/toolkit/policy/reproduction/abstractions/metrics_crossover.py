
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


class MetricsCrossover(SimpleOperator):
    '''
    An abstract convenience class which knows how to mate or "crossover"
    two parents, yielding one and only one instance of GeneticMaterial.
    This class handles the (rather abstract) GeneticMaterialOperator class
    appropriately.

    Subclasses override the crossover() method to create new child versions
    of their GeneticMaterial.

    In constract to SimpleCrossover, subclasses of MetricsCrossover are allowed
    to look at the metrics of mommy and daddy structures to aid in reproduction.

    MetricsCrossover implementations that operate as branch nodes in a structure
    have the option of repackaging the metrics structure handed to them
    so their child operators can focus on the metrics relevant to them.
    If this path is chosen, any parent metrics must be considered immutable.
    '''

    def crossover(self, mommy, daddy, mommy_metrics, daddy_metrics):
        '''
        An easier method for dealing with crossover yielding a single instance
        of a particular GeneticMaterial.

        :param mommy: 1st GeneticMaterial which is to be used as the basis
                for crossing.
        :param daddy: 2nd GeneticMaterial which is to be used as the basis
                for crossing.
        :param mommy_metrics: the immutable Metrics corresponding to the mommy
        :param daddy_metrics: the immutable Metrics corresponding to the daddy
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

        # Allow for parent_metrics to be None
        mommy_metrics = None
        daddy_metrics = None
        if parent_metrics is not None and \
                isinstance(parent_metrics, list):
            mommy_metrics = parent_metrics[0]
            daddy_metrics = parent_metrics[1]

        newbie = self.crossover(mommy, daddy, mommy_metrics, daddy_metrics)
        newbies = [newbie]
        return newbies

    def get_min_parents(self):
        '''
        :return: 2 Always. By definition a Crossover takes 2 parents.
        '''
        return 2
