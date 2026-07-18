
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

import copy
import math

from pyleafai.toolkit.policy.reproduction.abstractions.equally_weighted_genetic_material_generator \
    import EquallyWeightedGeneticMaterialGenerator


class OperatorSuiteHelper():
    '''
    A policy helper class that assists with choosing and executing
    GeneticMaterialOperators from an OperatorSuite based on the number
    of parents passed in.

    The main entry point to this class is create_from_suite().
    '''

    def __init__(self, random):
        '''
        Constructor.

        :param random: a Random number generator used for random decisions
        '''
        self._random = random

    def create_from_suite(self, parents, parent_metrics, suite, change_rate):
        '''
        Create a new value of a particular Type, based on an OperatorSuite
        and List of basis parents.

        :param parents: the List of zero to N parents to be used as bases
                for picking the correct kind of Operator, as well as for
                the being the bases for the Operator itself.
        :param parent_metrics: an immutable iterable collection of metrics
                associated with each respective parent.
        :param suite: the OperatorSuite to choose the Operator from,
                based on the number of parents.   If more than one
                Operator is registered in the Suite for a particular number
                of parents, an Operator is chosen randomly among the
                choices with equal weight.
        :param change_rate: the probability (0.0 - 1.0) that an Operator
                will instigate change from the parents passed in.
                If there are no parents (Creator case), this probability is
                ignored.
        :return: a new value created from an appropriate Operator chosen from
                the suite, based on the given parents
        '''

        next_double = self._random.next_double()
        next_int = self._random.next_int()

        parents = list(parents)
        value = self.create_from_suite_with_decsion(
                        parents, parent_metrics, suite, change_rate,
                        next_double, next_int)
        return value

    # pylint: disable=too-many-positional-arguments
    def create_from_suite_with_decsion(self, parents, parent_metrics,
                                       suite, change_rate, next_double, next_int):
        '''
        Same as create_from_suite() above, except with the random
        decision making predetermined.  This aids in testing.

        :param parents: the List of zero to N parents to be used as bases
                for picking the correct kind of Operator, as well as for
                the being the bases for the Operator itself.
        :param parent_metrics: an immutable iterable collection of metrics
                associated with each respective parent.
        :param suite: the OperatorSuite to choose the Operator from,
                based on the number of parents.   If more than one
                Operator is registered in the Suite for a particular number
                of parents, an Operator is chosen randomly among the
                choices with equal weight.
        :param change_rate: the probability (0.0 - 1.0) that an Operator
                will instigate change from the parents passed in.
                If there are no parents (Creator case), this probability is
                ignored.
        :param next_double: a randomly selected  from 0.0 - 1.0 which
                will be used in conjunction with the change_rate to make
                a decision.
        :param next_int: a randomly selected integer for use in
                determining which parent or operator might be picked.
        :return: a new value created from an appropriate Operator chosen from
                the suite, based on the given parents
        '''

        value = None

        # See if we should actually use an operator
        # When looking at creators (num_parents == 0), every field needs
        # to be populated, regardless of the field change rate.
        num_parents = len(parents)
        should_use_operator = (num_parents == 0) or (next_double < change_rate)

        if should_use_operator:
            value = self.pick_and_perform_operator(suite, parents,
                                                   parent_metrics, next_int)
        else:
            value = self.pick_a_parent(parents, next_int)
        return value

    def pick_a_parent(self, parents, next_int):
        '''
        Choose one from amongst a list of parents.

        :param parents: the List of 1 to N parents to be used as bases
                for picking the genetic material whole-cloth.
        :param next_int: a randomly selected integer for use in
                determining which parent is picked.
        :return: a value instance -- one of the parents
        '''

        num_parents = len(parents)

        # Pick a parent randomly in the list from which we will
        # get a value directly and use for the new child without
        # modification.
        which_parent = 0
        if num_parents > 1:
            which_parent = int(math.fabs(next_int % num_parents))

        # Use the value directly from the picked parent.
        value = parents[which_parent]

        return value

    def pick_and_perform_operator(self, suite, parents, parent_metrics, next_int):
        '''
        Pick an appropriate Operator from the Suite, given the number of
        parents passed in and perform its create_from() method with the
        given parents.

        :param suite: the OperatorSuite to choose the Operator from,
                based on the number of parents.   If more than one
                Operator is registered in the Suite for a particular number
                of parents, an Operator is chosen randomly among the
                choices with equal weight.
        :param parents: the List of zero to N parents to be used as bases
                for picking the correct kind of Operator, as well as for
                the being the bases for the Operator itself.
        :param parent_metrics: an immutable iterable collection of metrics
                associated with each respective parent.
        :param next_int: a randomly selected integer for use in
                determining which operator might be picked.
        :return: a value instance created from an appropriate operator from
                the suite given the number of parents.
        '''

        generator = EquallyWeightedGeneticMaterialGenerator(self._random, suite)

        field_spec = suite.get_evolved_parameter_spec()
        field_name = field_spec.get_name()

        num_parents = len(parents)

        my_op = self.pick_operator(generator, num_parents, next_int, field_name)
        # XXX Should this be deepcopy?
        immutable_parents = copy.copy(parents)
        immutable_metrics = copy.copy(parent_metrics)

        # Actually do the genetic operation
        op_results = my_op.create_from(immutable_parents, immutable_metrics)

        # Get the first (hopefully only) object returned from an
        # iterator as our newly created value for the field.
        value = op_results[0]

        return value

    def pick_operator(self, generator, n_parents,
                      next_int_for_operator, field_name):
        '''
        Pick an appropriate Operator from the Suite given the number of
        parents.

        :param generator: the generator corresponding to an OperatorSuite for a
                particular field of the structure, containing all possible
                Operators on the field.
        :param n_parents: the number of parent arguments for the Operator
                we are looking for.
        :param next_int_for_operator: a randomly selected integer for use in
                determining which operator might be picked.
        :param field_name: the String field_name corresponding to the OperatorSuite
                This is used for error reporting only.
        :return: a QuantifiableOperator that responds to the appropriate number
                of parents/operator arguments.  If more than one possibility
                is offered by the OperatorSuite, the QuantifiableOperator that
                is returned is chosen randomly among acceptable candidates.
        '''

        possible_ops = self.find_possible_operators(generator, n_parents,
                                                    field_name)

        my_op = generator.pick_operator(possible_ops, next_int_for_operator)

        return my_op

    def find_possible_operators(self, generator, num_parents, field_name):
        '''
        Find a List of possible Operators from an OperatorSuite given the
        number of parents we want to deal with.

        :param generator: the generator corresponding to an OperatorSuite for a
                particular field of the structure, containing all possible
                Operators on the field.
        :param num_parents: the number of parent arguments for the Operator
                we are looking for.
        :param field_name: the String field_name corresponding to the OperatorSuite
                This is used for error reporting only.
        :return: a list of potential QuantifiableOperators from the fieldSuite
                that fit the bill of the num_parents constraint
        '''

        possible_ops = generator.get_all_appropriate_operators(num_parents)

        # Throw an error if we did not find the operator with
        # the number of arguments we expected.
        if len(possible_ops) == 0:
            raise ValueError(
                f"No Operator found for field {field_name} with # args = {num_parents}")

        return possible_ops
