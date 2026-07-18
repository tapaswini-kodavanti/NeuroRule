
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

from pyleafai.toolkit.data.math.type_keywords import TypeKeywords

from pyleafai.toolkit.policy.reproduction.suitespecs.boolean_suite_spec_interpreter \
    import BooleanSuiteSpecInterpreter
from pyleafai.toolkit.policy.reproduction.suitespecs.dictionary_suite_spec_interpreter \
    import DictionarySuiteSpecInterpreter
from pyleafai.toolkit.policy.reproduction.suitespecs.list_suite_spec_interpreter \
    import ListSuiteSpecInterpreter
from pyleafai.toolkit.policy.reproduction.suitespecs.number_range_gaussian_suite_spec_interpreter \
    import NumberRangeGaussianSuiteSpecInterpreter
from pyleafai.toolkit.policy.reproduction.suitespecs.set_value_suite_spec_interpreter \
    import SetValueSuiteSpecInterpreter
from pyleafai.toolkit.policy.reproduction.suitespecs.suite_spec_interpreter \
    import SuiteSpecInterpreter
from pyleafai.toolkit.policy.reproduction.suitespecs.void_suite_spec_interpreter \
    import VoidSuiteSpecInterpreter


class TypeSuiteSpecInterpreter(SuiteSpecInterpreter):
    """
    Crossroads SuiteSpecInterpreter implementatation which takes any
    EvolvedParameterSpec and translates the spec data hierarchy into
    OperatorSuite hierarchy.

    All the other SuiteSpecInterpreters end up getting registered and used here,
    and it is this class which enables the recursion necessary to interpret
    specs calling for nested dictionaries (for instance).
    """

    def __init__(self):

        self.wildcard = None

        self._class_to_interpreter_map = {}

        self.register(TypeKeywords.DOUBLE, "EvolvedNumberSpec",
                      NumberRangeGaussianSuiteSpecInterpreter(),
                      [TypeKeywords.FLOAT])
        self.register(TypeKeywords.INTEGER, "EvolvedNumberSpec",
                      NumberRangeGaussianSuiteSpecInterpreter(),
                      [TypeKeywords.INT])
        self.register(TypeKeywords.VOID, "EvolvedStructureSpec",
                      VoidSuiteSpecInterpreter())

        self.register(self.wildcard, "EvolvedParameterSetSpec",
                      SetValueSuiteSpecInterpreter())
        self.register(TypeKeywords.BOOLEAN, self.wildcard,
                      BooleanSuiteSpecInterpreter())

        # Dictionary and List registration happen in here
        self.reregister(self)

    def interpret_spec(self, spec, obj):
        """
        Fulfill the superclass interface.

        :param spec: Some subclass of EvolvedParameterSpec defining the
                        data needed to create the OperatorSuite
        :param obj: a Random number generator used for random decisions
        :return: An OperatorSuite, as defined by the spec
        """

        random = obj
        # Create the key to find which interpreter to use by combining
        # the data class with the spec class
        data_class = spec.get_data_class()
        spec_class_name = spec.__class__.__name__

        tuple_key = (data_class, spec_class_name)
        interpreter = self._class_to_interpreter_map.get(tuple_key, None)

        # Try some wildcard combinations if that didn't work
        if interpreter is None:
            tuple_key = (self.wildcard, spec_class_name)
            interpreter = self._class_to_interpreter_map.get(tuple_key, None)

        if interpreter is None:
            tuple_key = (data_class, self.wildcard)
            interpreter = self._class_to_interpreter_map.get(tuple_key, None)

        if interpreter is None:
            raise ValueError(f"No interpreter for ({data_class}, {spec_class_name}) found")

        suite = interpreter.interpret_spec(spec, random)
        return suite

    def register(self, data_class_name, spec_class_name, spec_interpreter,
                 synonyms=None):

        # Keys to the map here are tuples of (<data_class>, <spec_class>)
        # A wild card of None can be used for either component, but not both.

        data_spec_tuple = (data_class_name, spec_class_name)
        self._class_to_interpreter_map[data_spec_tuple] = spec_interpreter

        if synonyms is not None and isinstance(synonyms, list):
            for synonym in synonyms:
                data_spec_tuple = (synonym, spec_class_name)
                self._class_to_interpreter_map[data_spec_tuple] = \
                    spec_interpreter

    def reregister(self, alt_type_suite_spec_interpreter):
        """
        Reregister the type parser with other SuiteSpecParsers that require
        the instance.

        Overriding subclasses that handle domain-specific types will
        want to override this method as well, and also to be sure to
        call this superclass method.

        :param alt_type_suite_spec_parser: The TypeSpecParser to register
            known SpecParsers with.
        """

        self.register(TypeKeywords.DICTIONARY, "EvolvedStructureSpec",
                      DictionarySuiteSpecInterpreter(
                            alt_type_suite_spec_interpreter))
        self.register(TypeKeywords.LIST, "EvolvedListSpec",
                      ListSuiteSpecInterpreter(
                            alt_type_suite_spec_interpreter))
