
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

class OperatorSuite():
    '''
    A class which, given an EvolvedParameterSpec specification,
    can put together a suite of QuantifiableOperators to
    assist in evolving that primitive.
    '''

    def __init__(self, evolved_parameter_spec):
        '''
        Constructor.

        :param evolved_parameter_spec:
            an EvolvedParameterSpec object specifying relevant aspects of the
            evolved parameter for reproduction.
        '''
        self._evolved_parameter_spec = evolved_parameter_spec
        self._operators = []

    def register(self, operator):
        '''
        Intended to be called by subclasses only.
        :param operator: the QuantifiableOperator to register with the suite.
        '''
        self._operators.append(operator)

    def get_evolved_parameter_spec(self):
        '''
        :return: the EvolvedParameterSpec used for this suite instance.
        '''
        return self._evolved_parameter_spec

    def get_operators(self):
        '''
        :return: an immutable copy of the list of quantifiable operators
            handled by this suite instance.
        '''
        return list(self._operators)
