
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

class IdentityKeys():
    '''
    Interface defining string constants of keys that would be available
    in the Identity dictionary.
    '''

    # A String representing a unique identifier (unique at least within
    # the experiment) for the Individual.
    UNIQUE_ID = 'unique_id'

    # A String name corresponding to the domain for an experiment.
    # This needs to be unique enough within the context of multiple domains.
    DOMAIN_NAME = 'domain_name'

    # A String name corresponding to an experiment version.
    # This needs to be unique enough within the context of a single domain.
    EXPERIMENT_VERSION = 'experiment_version'

    # An immutable list of the unique id Strings of any immediate parents
    # contributing genetic material to the creation of an offspring.
    # This list can be empty, but not None.
    ANCESTOR_IDS = 'ancestor_ids'

    # The largest number of generations from a pure random creation operation
    # needed to arrive at the corresponding Individual.
    ANCESTOR_COUNT = 'ancestor_count'

    # The generation number when the corresponding Individual was first created.
    BIRTH_GENERATION = 'birth_generation'
