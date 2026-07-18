
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


class OringTerminator(ContainingTerminator):
    """
    An implementation of a ContainingTerminator where the shouldTerminate()
    implementation will return True if any one of the contained Terminators
    returns True.
    """

    def should_terminate(self):

        terminators = self.get_terminators()

        do_terminate = False
        for terminator in terminators:
            one_should_terminate = terminator.should_terminate()
            do_terminate = do_terminate or one_should_terminate

        return do_terminate
