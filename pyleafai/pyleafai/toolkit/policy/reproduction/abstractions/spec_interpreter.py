
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


class SpecInterpreter():
    """
    Interface for interpreting an EvolvedParameterSpec of some kind
    by way of some object.

    All implementations are expected to be stateless with respect to
    their own member variables.
    """

    def interpret_spec(self, spec, obj):
        """
        :param spec: Some subclass of EvolvedParameterSpec defining the
                        data needed to interpret the object
        :param obj: the object that is used as an aid to interpreting
                    the spec.
        :return: An object, defined by the spec, whose instance is interpreted
                 from the spec and the object passed in
        """
        raise NotImplementedError
