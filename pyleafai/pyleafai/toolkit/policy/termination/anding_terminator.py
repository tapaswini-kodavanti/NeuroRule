
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

from pyleafai.toolkit.policy.termination.containing_terminator \
    import ContainingTerminator


class AndingTerminator(ContainingTerminator):
    """
    An implementation of a ContainingTerminator where the should_terminate()
    implementation will return true only if all of the contained Terminators
    return true.
    """

    def should_terminate(self):

        terminators = self.get_terminators()

        should_terminate = True
        for terminator in terminators:
            one_should_terminate = terminator.should_terminate()
            should_terminate = should_terminate and one_should_terminate

        return should_terminate
