
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

from pyleafai.toolkit.policy.reproduction.structures.abstract_structure_operator_helper \
    import AbstractStructureOperatorHelper


class DictionaryStructureOperatorHelper(AbstractStructureOperatorHelper):
    '''
    A class which assists with the abstract and generic mechanics of
    creating dictionaries via the abstract Structure Operators in this
    same package.
    '''

    def create_one_from_parents(self, parents, parent_metrics):
        '''
        Create an instance of structure storage type (a Dictionary)
        from a list of parents.

        :param parents:
                a list of parents to use as the bases for the genetic
                operator. The size of this list determines what kind of
                genetic operator to use. If there is more than one genetic
                operator for any given field, the one to use is picked at
                random.
        :param parent_metrics: Metrics from parents
        :return: a new instance of the structure storage type, created
                from the genetic operator selected on a field by field basis.

                Can return None only if the structure type is Void,
                as None is the only legal value for anything of type Void,
                and the Void class has no constructor.
        '''

        # Call the method with decision so the tests call that method
        # for deterministic results
        number_of_parents = len(parents)

        # By default, no parents so set the parent_to_choose_extra to None
        parent_to_choose_extra = None
        if number_of_parents > 0:

            which_parent = self.get_random().next_int(number_of_parents)
            parent_to_choose_extra = parents[which_parent]

        new_one = self.create_from_parents_with_decision(parents, parent_metrics,
                                                         parent_to_choose_extra)
        return new_one

    def create_from_parents_with_decision(self, parents, parent_metrics,
                                          chosen_parent):
        '''
        Create an instance of structure storage type from a list of parents
        and populate the un-evolved fields from the chosen parent.

        This is added so tests can invoke this to get the deterministic results.

        :param parents: a list of parents
        :param parent_metrics: Metrics from parents
        :param chosen_parent: chosen parent to extract the un-evolved fields.
        :return: a new instance of structure storage type
        '''

        # First invoke the super class' create_one_from_parents
        newbie = super().create_one_from_parents(parents, parent_metrics)

        # Return None if the super class returned None
        if newbie is None:
            return newbie

        # If the number of parents is zero, nothing to be added, return newbie
        if len(parents) == 0 or chosen_parent is None:
            return newbie

        # Pass-through additional non-evolved fields from the parents to the
        # newbie.

        # First determine the union set of dictionary keys across all parents.
        combined_keys = set()
        for one_parent in parents:
            one_parent_keys = one_parent.keys()
            combined_keys.update(one_parent_keys)

        # Remove the ones that have been in the OperatorSuite and have already
        # been populated in the newbie
        newbie_keys = newbie.keys()
        combined_keys.difference_update(newbie_keys)

        # For the remaining set of keys, use the fields from the chosen_parent
        # and add those fileds to the newbie
        for field_name in combined_keys:
            field_value = chosen_parent.get(field_name, None)
            newbie[field_name] = field_value

        return newbie

    def instantiate_one(self):
        '''
        :return: a new, empty, properly typed map/dictionary
        '''
        # Might seem ridiculous in Python, but the Java had a lot more hoops
        # to jump through
        return {}

    def create_one(self, field_values):
        '''
        Given a list of field values, creates a single instance
        of the Java class associated with the correct storage for the
        implementation.

        :param field_values: an array of Objects comprising an ordered list
                of field values to create a fully populated instance for this
                structure storage type.  The order of the list of objects
                corresponds to the order of the fields in the field_suites
                passed into the constructor.
        :return: a new structure storage type instance, initialized according
                to the field_values.
        '''

        newbie = self.instantiate_one()

        # Now iterate through the field_suites and get their names
        # as keys to populate the map
        field_value_index = 0
        for field_suite in self.get_field_suites():

            field_suite_name = \
                field_suite.get_evolved_parameter_spec().get_name()

            field_value = field_values[field_value_index]
            newbie[field_suite_name] = field_value

            field_value_index = field_value_index + 1

        return newbie

    def get_field_value(self, instance, field_spec):
        '''
        Get the field value from the given instance for the field_spec
        passed in.

        :param instance: the instance of the map structure which owns the field
                       value we are looking for.
        :param field_spec: the EvolvedParameterSpec structure with the class
                    and name of the field.
        :return: the value of the field, as an Object, on the given instance.
        '''

        # Get the key for the map from the field_spec's name
        field_name = field_spec.get_name()
        value = instance.get(field_name, None)

        return value
