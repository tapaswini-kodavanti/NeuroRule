
# Copyright (C) 2019-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# esp-service Software in commercial settings.
#
# END COPYRIGHT
"""
See class comment for details.
"""

from typing import Dict
from typing import List

from pyleafai.toolkit.policy.math.generation_counter import GenerationCounter
from pyleafai.toolkit.policy.reproduction.identity.basis_child_identity_operator \
    import BasisChildIdentityOperator
from pyleafai.toolkit.policy.reproduction.identity.identity_operator import IdentityOperator

from esp_service.reproduction.originator.originator import Originator
from esp_service.reproduction.uniqueids.generation_scoped_unique_identifier_generator \
    import GenerationScopedUniqueIdentifierGenerator


class EspIdentityOperator(IdentityOperator):
    """
    Generates the Identity dictionary given the parents' individual dictionaries
    as long as those have identity dictionaries in them.
    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self, config: Dict[str, object],
                 new_candidate_id: str,
                 generation_counter: GenerationCounter = None,
                 experiment_id: str = None,
                 originator: Originator = None):
        """
        Constructor.

        :param config: The dictionary of experiment parameters
        :param new_candidate_id: The string id of the new candidate
        :param generation_counter: A GenerationCounter instance that reports
                the current generation
        :param experiment_id: The unique identifier for the experiment
        :param originator: The Originator instance that accumulated
                origin information during reproduction.
        """
        self._config = config
        self._new_candidate_id = new_candidate_id

        self._generation_counter = generation_counter

        if self._generation_counter is None:
            # This ends up always defaulting to same generation id
            generation_id = 0
            self._generation_counter = GenerationScopedUniqueIdentifierGenerator(
                generation_id)

        self._experiment_id = experiment_id
        self._originator = originator

    def create_from(self, parents: List[Dict[str, object]],
                    parent_metrics=None) -> List[Dict[str, object]]:
        """
        Create the identity dictionary for the new candidate.
        Note that the argument types here are asymmetric.
        What goes in is parent ESP individual dictionaries.
        What comes out is an identity

        :param parents: A list of parent individual dictionaries
        :param parent_metrics: Used only to fulfill parent interface.
        :return: A list containing a single identity dictionary for the new candidate
        """
        identity = self.create_one(parents)
        return [identity]

    def create_one(self, parents):
        """
        Creates a single identity dictionary for the new candidate.
        Note that the argument types here are asymmetric.
        What goes in is parent ESP individual dictionaries.
        What comes out is an identity

        :param parents: A list of parent individual dictionaries
        :return: A single identity dictionary for the new candidate
        """
        parent_identities = []
        for parent in parents:
            parent_identity = parent.get("identity", None)

            # Allow for identities not to be specified.
            # This will happen in tests.
            if parent_identity is not None:
                parent_identities.append(parent_identity)

        # Assemble the identity dictionary by first adding
        # what comes stock from pyleafai.
        identity_operator = BasisChildIdentityOperator(self._generation_counter)
        identity_results = identity_operator.create_from(parent_identities, None)
        identity = identity_results[0]

        # See about the origin, and add it to the identity dictionary
        origin = self._originator.get_origin()
        if origin is None or len(origin) == 0:
            # Default if no origin detected
            origin = "(none)"

        # See about the domain name.
        empty_dict = {}
        domain_config = self._config.get("domain_config", empty_dict)
        domain_name = domain_config.get("domain_name", None)

        # Fill in some blanks
        identity["origin"] = origin
        identity["experiment_version"] = self._experiment_id
        identity["domain_name"] = domain_name
        identity["unique_id"] = self._new_candidate_id

        return identity

    def get_key(self):
        """
        Normally this is used to identify a field *within* the Identity
        dictionary, but for now, to fulfill the interface, simply return
        the key we use for the identity dictionary in the ESP Individual
        dictionaries.

        :return: the string key for the identity field
        """
        return "identity"
