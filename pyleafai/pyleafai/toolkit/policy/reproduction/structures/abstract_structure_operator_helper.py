
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

from pyleafai.toolkit.data.math.type_keywords import TypeKeywords


class AbstractStructureOperatorHelper():
    '''
    A class which assists with the abstract and generic mechanics of
    creating structures (abstractly) via the structure Operators
    in this package.

    The specifics of instance creation and field storage are left as
    implementation details.
    '''

    def __init__(self, random, evolved_structure_spec, field_suites,
                 field_change_rate=1.0):
        '''
        Constructor.

        :param random:  a random number generator used for random decisions
        :param evolved_structure_spec: the EvolvedParameterSpec describing the
                    structure.
        :param field_suites: a List of OperatorSuites, where each entry
                    corresponds to the suite to be used for a particular
                    field in the structure to evolve.

                    For classes in particular, the order of these Suites
                    must match the order of the corresponding arguments in
                    the class's constructor.
        :param field_change_rate: the probability that any given field will
                    undergo some kind of change by a GeneticOperator.
                    The default is 1.0.
        '''
        self._random = random
        self._structure_class = evolved_structure_spec.get_data_class()
        self._field_suites = field_suites
        self._field_change_rate = field_change_rate

    #
    # Subclass interface
    #

    def create_one(self, field_values):
        '''
        Given a list of field values, creates a single instance
        of the class associated with the correct storage for the
        implementation.

        :param field_values: an array of Objects comprising an ordered list
                of field values to create a fully populated instance for this
                structure type.  The order of the array of objects corresponds
                to the order of the fields in the field_suites passed into
                the constructor.  This is so class construction has
                a chance of using reflection to find the correct constructor
                to call.
        :return: a new structure storage instance, initialized according to the
                field_values.
        '''
        raise NotImplementedError

    def get_field_value(self, instance, field_spec):
        '''
        :param instance: the instance of the structure storage instance
                which owns the field value we are looking for.
        :param field_spec: the EvolvedParameterSpec with the class
                and name and class of the field.
        :return: the value of the field, as an Object, on the given instance.
        '''
        raise NotImplementedError

    def get_structure_class(self):
        '''
        :return: the class (string) for storage structure,
                as passed in the constructor.
        '''
        return self._structure_class

    def get_field_suites(self):
        '''
        :return: the ordered List of OperatorSuites for each field in the
                structure.
        '''
        return self._field_suites

    def get_random(self):
        '''
        :return: the Random number generator to subclasses
        '''
        return self._random

    def create_one_from_parents(self, parents, parent_metrics):
        '''
        External entry point used by structure Operators.

        :param parents:
                a list of parents to use as the bases for the genetic
                operator. The size of this list determines what kind of
                genetic operator to use. If there is more than one genetic
                operator for any given field, the one to use is picked at
                random.
        :param parent_metrics: The metrics associated with the parents
        :return: a new instance of the structure storage type, created from
                the genetic operator selected on a field by field basis.

                Can return None only if the structure type is Void,
                as None is the only legal value for anything of type Void,
                and the Void class has no constructor.
                Typically this Void business would only happen in an abstract
                evolvable structure representation.

        Raises an exception if:
            * A suitable constructor does not exist for structure_class,
                meaning the order of the constructor arguments does not
                follow the order in the member OperatorSuites.
                Note that arguments of type Void are skipped in this ordering.
        '''

        # Handle the Void class case.  Void has no visible constructor.
        if TypeKeywords.VOID == self._structure_class:
            return None

        field_values = self.create_ordered_field_values(parents, parent_metrics)
        return self.create_one(field_values)

    def find_possible_operators(self, field_suite, num_parents):
        '''
        :param field_suite: an OperatorSuite for a particular field of the
                structure, containing all possible Operators on the field.
        :param num_parents: the number of parent arguments for the Operator
                we are looking for.
        :return: a list of potential QuantifiableOperators from the field_suite
                that fit the bill of the num_parents constraint
        '''

        possible_ops = []

        # Find operators for the field that has the right number of args
        for qop in field_suite.get_operators():
            if qop.get_min_parents() == num_parents:
                possible_ops.append(qop)

        # Throw an error if we did not find the operator with
        # the number of args we expected.
        if len(possible_ops) == 0:

            field_spec = field_suite.get_evolved_parameter_spec()
            field_name = field_spec.get_name()
            raise ValueError(
                f"No Operator found for field {field_name} with # args = {num_parents}")

        return possible_ops

    def pick_operator(self, field_suite, n_parents):
        '''
        :param field_suite: an OperatorSuite for a particular field of the
                structure, containing all possible Operators on the field.
        :param n_parents: the number of parent arguments for the Operator
                we are looking for.
        :return: a QuantifiableOperator that responds to the appropriate number
                of parents/operator arguments.  If more than one possibility
                is offered by the OperatorSuite, the QuantifiableOperator that
                is returned is chosen randomly among acceptable candidates.
        '''

        possible_ops = self.find_possible_operators(field_suite, n_parents)

        # Use the first listed operator as our default pick.
        my_op = possible_ops[0]

        # If we have more than one op that fits the bill,
        # pick randomly among them.
        # XXX Weights would go in here.
        n_ops = len(possible_ops)
        if n_ops > 1:
            which_op = self._random.next_int(n_ops)
            my_op = possible_ops[which_op]

        return my_op

    def create_ordered_field_values(self, parents, parent_metrics):
        '''
        :param parents: the list of homogeneously typed parents for which we
                are looking to use as genetic operator bases.
        :param parent_metrics: The metrics associated with the parents
        :return: an array of new Object instances corresponding to values
            for each field in the list of field_suites, in the order that they
            appear in the field_suites list. These results are intended to be
            passed to the create_one() implementation.

        Note: per-field randomization policy comes from the field_suite
            instances themselves by means of looking for an Operator that
            takes 0 parents.
        '''

        num_args = len(parents)

        # Find the ordered list of constructor arguments.
        args_list = []
        for field_suite in self._field_suites:

            # Check for the case of a class being the Void class.
            # We do not expect an argument in the constructor for this type
            # because no one can construct an instance of type Void.
            data_class = \
                    field_suite.get_evolved_parameter_spec().get_data_class()
            if TypeKeywords.VOID == data_class:
                continue

            # Make a list of the parents to use for the field's operation.
            field_parents = []
            for parent in parents:

                field_spec = field_suite.get_evolved_parameter_spec()

                parent_value = self.get_field_value(parent, field_spec)
                field_parents.append(parent_value)

            # XXX Worth noting that there is no opportunity to reach in
            #     and get field-specific parent metrics. Probably OK.

            # See if we should actually use an operator
            # When looking at creators (num_args == 0), every field needs
            # to be populated, regardless of the field change rate.
            should_use_operator = (num_args == 0) or \
                (self._random.next_double() < self._field_change_rate)

            field_value = None
            if should_use_operator:

                # XXX There is an opportunity to use
                #   EquallyWeightedGenericMaterialGenerator here to
                #   consolidate logic. In doing that, pick_operator()
                #   and find_possible_operators() can be removed here.

                my_op = self.pick_operator(field_suite, num_args)
                immutable_field_parents = copy.copy(field_parents)

                # Actually do the genetic operation
                op_results = my_op.create_from_objects(immutable_field_parents,
                                                       parent_metrics)

                # Get the first (hopefully only) object returned from an
                # iterator as our newly created value for the field.
                field_value = op_results[0]

            else:

                # Pick a parent randomly in the list from which we will
                # get a value directly and use for the new child without
                # modification.
                num_parents = len(parents)
                which_parent = self._random.next_int(num_parents)

                # Use the value directly from the picked parent.
                field_value = field_parents[which_parent]

            # Add to our argument list to send to the constructor.
            args_list.append(field_value)

        return args_list
