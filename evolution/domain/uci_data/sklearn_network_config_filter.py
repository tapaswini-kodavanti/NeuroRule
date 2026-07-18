
from typing import Dict

# pylint: disable=unused-import
from sklearn import datasets  # noqa: F401

from leaf_common.config.config_filter import ConfigFilter
from domain.uci_data.network_config_filter import NetworkConfigFilter


class SklearnNetworkConfigFilter(ConfigFilter):
    """
    Reads in an sklearn data set and modifies the config according
    to that dataset's inputs (feature names) and outputs (targets).
    """

    def __init__(self):
        """
        Constructor
        """
        self.data_set = None

    def filter_config(self, basis_config: Dict[str, object]) \
            -> Dict[str, object]:
        """
        Filters the given basis config.

        Ideally this would be a Pure Function in that it would not
        modify the caller's arguments so that the caller has a chance
        to decide whether to take any changes returned.

        :param basis_config: The config dictionary to act as the basis
                for filtering
        :return: A config dictionary, potentially modified as per the
                policy encapsulated by the implementation
        """

        # Get various incarnations of the domain-specific config
        # #1 - modern way: using domain_config key.
        #       This conforms to what ENN does too.
        domain_config = basis_config.get("domain_config", None)
        if domain_config is None:
            # #2 - old way: using domain key
            # #3 - fall back to the given config itself.
            #       for now, this makes distributed evaulation work
            domain_config = basis_config.get("domain", basis_config)

        # Load the data set
        self.data_set = self._load_sklearn_dataset(domain_config)

        # Create network specification inputs and outputs based on the data
        config_filter = NetworkConfigFilter(self.data_set.feature_names,
                                            self.data_set.target_names)
        new_config = config_filter.filter_config(basis_config)
        return new_config

    def get_data_set(self):
        """
        :return: the data set read in from the call to filter_config()
        """
        return self.data_set

    def _load_sklearn_dataset(self, domain_config):
        """
        Loads the named sklearn data set in the domain config

        :param domain_config: The domain config section from the
                top-level config
        :return: an sklearn data set
        """
        dataset_string = domain_config.get("data_set")
        eval_string = "datasets." + dataset_string + "()"

        # This is not the safest thing to do, but it's good for our purpose
        # pylint: disable=eval-used
        data_set = eval(eval_string)
        return data_set
