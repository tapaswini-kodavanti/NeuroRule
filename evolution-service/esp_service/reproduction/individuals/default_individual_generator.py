
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
from pyleafai.toolkit.policy.reproduction.individuals.individual_generator import IndividualGenerator
from pyleafai.toolkit.policy.reproduction.uniqueids.unique_identifier_generator import UniqueIdentifierGenerator

from esp_service.adapters.interface.representation_service_adapter import RepresentationServiceAdapter
from esp_service.reproduction.originator.originator_factory import OriginatorFactory
from esp_service.reproduction.individuals.esp_identity_operator import EspIdentityOperator


class DefaultIndividualGenerator(IndividualGenerator):
    """
    IndividualGenerator implementation for the default, aboriginal method of
    reproducing individuals that ESP originally had. This specifically does
    a crossover of 2 parents, and then a mutation of the baby.

    Also worth noting that the "Individual" here has an ESP-specific definition
    which is a dictionary that contains the following 3 keys:
        "id":               The Unique Identifier for the individual (string)
        "interpretation":   The actual model for the given representation
                            that would be sent back to the client. Depending on
                            the representation, this may or may not be the same
                            as the genetic material used to create the candidate.
        "identity":         A dictionary containing info as to how the
                            individual came into being
    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self, config: Dict[str, object],
                 adapter: RepresentationServiceAdapter,
                 generation_counter: GenerationCounter = None,
                 id_generator: UniqueIdentifierGenerator = None,
                 experiment_id: str = None):
        """
        Constructor.

        :param config: The dictionary of experiment parameters
        :param adapter: The RepresentationServiceAdapter implementation
                to be used embodying all representation-specific behavior.
        :param generation_counter: A GenerationCounter instance that reports
                the current generation
        :param id_generator: A UniqueIdentifierGenerator implementation that
                knows how to come up with ids unique to the experiment.
        :param experiment_id: The unique identifier for the experiment
        """
        self._config = config
        self._adapter = adapter
        self._generation_counter = generation_counter
        self._id_generator = id_generator
        self._experiment_id = experiment_id
        self._generation_counter = generation_counter

    def create_from_individuals(self, parents) -> List[Dict[str, object]]:
        """
        Creates children from the passed parents. In other words,
        create new Individual instances from the passed ones, if any.

        :param parents: an immutable collection of Individuals that can be
            used to create new Individuals. Can be an empty collection,
            but not None.

            Since subclasses are meant to be dealing with Individuals,
            those constructs already have metrics on them and parent_metrics
            will largely be ignored.

        :return: a *list* of child individuals in dictionary form
        """

        # Break up individual structures into useful lists of components
        parent_ids = []
        parent_gm = []
        for parent in parents:
            parent_ids.append(parent['id'])
            parent_gm.append(parent['interpretation'])

        # Create a new id for the baby
        baby_id = None
        if self._id_generator is not None:
            baby_id = self._id_generator.next_unique_identifier()

        # Set up the origin reporting
        originator = OriginatorFactory.create_originator(self._config,
                                                         parent_ids=parent_ids)

        # Do reproduction
        if len(parents) >= 2:

            # Crossover first, if possible...
            # Current crossover_genetic_material() contract actually takes
            # genetic material instances as arguments
            baby_weights = self._adapter.crossover_genetic_material(
                parent_gm, originator, self._config)

        elif len(parents) == 1:
            # While this path is not taken by any extant ESP code...
            # it does fill in a gap with respect to the callable interface.
            baby_weights = parent_gm[0]

        # Either always mutate (after potential crossover above) or create
        if len(parents) >= 1:
            # ... then always Mutate
            # Current mutate_genetic_material() contract does not actually take
            # an individual but only the 'interpretation'
            baby_weights = self._adapter.mutate_genetic_material(
                baby_weights, originator, self._config)
        else:
            # Call the creator

            # We need to send in the newly minted unique id to the creator
            # because NNWeights has this custom_init hack that depends on it
            # in its create.py _create_weights() method.  Most normal
            # Creators would not care about parent_ids of a newly created
            # genetic material instance, so it's OK for now.
            parent_ids = [baby_id]
            originator = OriginatorFactory.create_originator(self._config,
                                                             parent_ids=parent_ids)

            baby_weights = self._adapter.create_genetic_material(self._config, originator)

        if self._config["evolution"].get("diversity", None) == "different_from_parents":
            # Keep mutating until baby is different from both mom and dad
            nb_additional_mutations = 0
            while not self.is_different_from_parents(baby_weights, parent_gm):
                baby_weights = self._adapter.mutate_genetic_material(
                    baby_weights, None, self._config)
                nb_additional_mutations += 1
            if nb_additional_mutations > 0:
                originator.append_origin("additional_mutations",
                                         "-" + str(nb_additional_mutations))

        # Set up the identity operator
        identity_operator = EspIdentityOperator(self._config, baby_id,
                                                generation_counter=self._generation_counter,
                                                experiment_id=self._experiment_id,
                                                originator=originator)
        # This guy is asymmetric. Takes individuals, but returns identity.
        identity = identity_operator.create_one(parents)

        # Assemble what ESP requires as an individual
        baby = {
            'id': baby_id,
            'interpretation': baby_weights,
            'identity': identity
        }

        # We are only making a single child but interface requires us
        # to send back a list
        children = [baby]
        return children

    def is_different_from_parents(self, baby_weights, parent_gms):
        """
        :param baby_weights: the weights of a children from the couple
        :param parents: a list of parent genetic material
        :param experiment_params: the experiment parameters
        :param adapter: The RepresentationServiceAdapter for the representation
        :return: true if the baby weights lead to a different behavior that both its dad and mom.
        """
        for parent_gm in parent_gms:
            if self._adapter.is_same_behavior(baby_weights, parent_gm, self._config):
                # Same as parent. No need to check any other parents
                return False

        # Different from both mommy and daddy
        return True
