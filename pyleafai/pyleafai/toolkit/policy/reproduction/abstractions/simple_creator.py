
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


class SimpleCreator(SimpleOperator):
    '''
    An abstract convenience class which knows how to create one and only
    one instance of GeneticMaterial, handling the (rather abstract)
    GeneticMaterialOperator class appropriately.

    Subclasses override the create() method to create their GeneticMaterial.
    '''

    def create(self):
        '''
        An easier method for dealing with creating a single instance of a
        particular GeneticMaterial.

        :return: a new (perhaps randomized, perhaps not) instance of the
            GeneticMaterial
        '''
        raise NotImplementedError()

    def create_from(self, parents, parent_metrics):
        '''
        Creates a single instance of GeneticMaterial,
        ignoring any parents passed in.
        @see SimpleOperator.create_from()
        '''

        #  We ignore the parents.  Just like my kids.
        newbie = self.create()
        newbies = [newbie]
        return newbies

    def get_min_parents(self):
        '''
        :return: 0 Always. By definition a Creator takes no parents.
        '''
        return 0
