
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

import math

from pyleafai.api.policy.reproduction.genetic_material_operator \
    import GeneticMaterialOperator

from pyleafai.toolkit.policy.reproduction.abstractions.quantifiable_operator \
    import QuantifiableOperator
from pyleafai.toolkit.policy.reproduction.abstractions.operator_suite \
    import OperatorSuite


class EquallyWeightedGeneticMaterialGenerator(GeneticMaterialOperator):
    '''
    Reproduction policy based on a map containing lists of like-parented
    QuantifiableOperators (which are GeneticMaterialOperators
    that can tell us how many parents they require and how many offspring
    they spit out).

    As soon as we know how many parents we need to produce a new instance
    of GeneticMaterial, the create_from() implementation here chooses among
    the candidate Operators with the appropriate number of
    parents at random. The chosen Operator is used to create a new
    GeneticMaterial instance.

    Some genetic material might consist of a hierarchy of other data-only
    classes acting as GeneticMaterial, but we only worry about the top-level
    structure in all entry points here.  We assume that the top-level operators
    registered here know how to take care of evolving the other material
    further down in the hierarchy.
    '''

    def __init__(self, random, operator_suite=None):
        '''
        Constructor.

        :param random: a Random number generator for making random decisions.
        :param operator_suite:
                an OperatorSuite containing any GeneticMaterialOperators
                to be used to create new GeneticMaterial instances from any
                number of parents.  Default of None does no registration.
        '''

        self._random = random

        # Here we have a Map where the key corresponds to an Integer describing
        # how many parents we want to deal with.
        #
        # Associated with each key into the Map, we have a value which is a list
        # which contains all the GeneticOperators we want to use for that number
        # of parents.
        self._operators = {}

        if operator_suite is not None:
            self.register(operator_suite)

    #
    # Subclass/Operator Registration interface
    #

    def register(self, operator, min_parents=None):
        '''
        Intended to be called in a subclass's constructor to register a
        particular Operator with this class that can potentially be chosen
        by a combination of the min_parents provided for it and the
        implementation of pick_operator() method in this class.

        :param operator:
                  the operator to register
        :param min_parents:
                  the minimum number of parents applicable to the operator.
        '''

        # Case if someone calls this method with an iterable
        if isinstance(operator, (list, set)):

            self.register_operator_set(operator)
            return

        # Case if someone calls this method with an OperatorSuite
        if isinstance(operator, OperatorSuite):
            operator_set = operator.get_operators()
            self.register_operator_set(operator_set)
            return

        # Determine the value to use for num_parents
        # that we will put in the map.
        use_min_parents = min_parents
        if use_min_parents is None:
            if isinstance(operator, QuantifiableOperator):
                use_min_parents = operator.get_min_parents()
            else:
                raise ValueError("Cannot determine min_parents")

        # See if we can get an existing list
        ops = self._operators.get(use_min_parents, None)

        # Create a list if we need one and add it.
        if ops is None:
            ops = []
            self._operators[use_min_parents] = ops

        # Add to the list that is already in the map
        ops.append(operator)

    def register_operator_set(self, operator_set):
        '''
        :param operator_set a Collection of QuantifiableOperators to register
        '''
        for operator in operator_set:
            self.register(operator, None)

    #
    # GeneticMaterialOperator implementation
    #

    def create_from(self, parents, parent_metrics):
        '''
        Creates children from the passed parents.
        In other words, create new instances of GeneticMaterial from the
        passed parents, if any.

        :param parents: an ImmutableCollection of GeneticMaterial that can be
              used to create new GeneticMaterial. Can be an empty collection.
        :param parent_metrics: an immutable iterable collection of metrics
            associated with each respective parent.
        :return: a Collection of children
        '''
        next_int = self._random.next_int()
        return self.create_from_with_decision(parents, parent_metrics, next_int)

    def create_from_with_decision(self, parents, parent_metrics, next_int):
        '''
        An internal, deterministic version of create_from() above to allow
        for better testability.

        :param parents: an ImmutableCollection of GeneticMaterial that can be
              used to create new GeneticMaterial. Can be an empty collection.
        :param parent_metrics: an immutable iterable collection of metrics
            associated with each respective parent.
        :param next_int: a randomly selected integer for use in
                determining which operator might be picked.
        :return: a Collection of children
        '''

        num_parents = len(parents)

        # Given the number of parents in the list, find the appropriate
        # set of Operators to use.
        appropriate_operators = self.get_all_appropriate_operators(num_parents)

        # Did we even have a list?
        if appropriate_operators is None:
            return None

        # Pick one of the Operators at random.
        operator = self.pick_operator(appropriate_operators, next_int)

        # Perform the operation
        all_new_material = operator.create_from(parents, parent_metrics)

        return all_new_material

    #
    # Helper Methods
    #

    def get_all_appropriate_operators(self, num_parents):
        '''
        Given the GeneticMaterialOperators that have been registered with
        this class, return a List of Operators that are appropriate for use
        with a particular number of parents.

        :param num_parents: the number of parents that any Operator returned
                by the query should be able to handle
        :return: the List of Operators that are appropriate for use
                with the given num_parents.
        '''

        appropriate_operators = self._operators.get(num_parents, None)
        return appropriate_operators

    def pick_operator(self, operator_list, next_int):
        '''
        Choose an operator from a list at random.
        This is where the "equally weighted" part of the name of this class
        comes in.  Each operator in the list is given an equal chance of
        being picked.

        Subclasses might choose to override this for a different policy

        :param operator_list: a List of Operators to choose from
        :param next_int: a randomly selected integer for use in determining
                which parent or operator might be picked.
        :return: a GeneticMaterialOperator from the given operators List
        '''

        # Use the first listed operator as our default pick
        my_op = operator_list[0]

        # If we have more than one op that fits the bill,
        # pick randomly among them.
        n_ops = len(operator_list)
        if n_ops > 1:
            # XXX This is a place where weights would come in.
            which = int(math.fabs(next_int % n_ops))
            my_op = operator_list[which]

        return my_op
