"""
See class comments for details
"""

import copy

from typing import Dict
from typing import List

from leaf_common.config.config_filter import ConfigFilter


class NetworkConfigFilter(ConfigFilter):
    """
    Modifies a config to add inputs and outputs based on the
    reading in of an sklearn data set.
    """

    def __init__(self, feature_names: List[str], target_names: List[str]):
        """
        Constructor.

        :param feature_names: The list of feature names comprising the inputs
                for the base model network specification.
        :param target_names: The list of target names comprising the outputs
                for the base model network specification.
        """
        self.feature_names = feature_names
        self.target_names = target_names

    def filter_config(self, basis_config: Dict[str, object]) \
            -> Dict[str, object]:

        # Make a copy so as not to *have* to modify the inputs
        # if caller doesn't want to.
        config = copy.deepcopy(basis_config)

        # Find the network config part of the larger config
        if 'network' not in config.keys():
            config['network'] = {}
        network_config = config['network']

        # Do the work
        if 'inputs' not in network_config:
            network_config['inputs'] = self._build_network_inputs()
        if 'outputs' not in network_config:
            network_config['outputs'] = self._build_network_outputs()
        # network_config['inputs'] = self._build_network_inputs()
        # network_config['outputs'] = self._build_network_outputs()

        return config

    def _build_network_inputs(self) -> List[Dict[str, object]]:
        # Using feature_names to generate inputs
        inputs = []
        for feature_name in self.feature_names:
            inputs.append({
                "name": feature_name,
                "size": 1,
                "values": [
                    "float"
                ]
            })
        return inputs

    def _build_network_outputs(self) -> List[Dict[str, object]]:
        # Using target_names for outputs:
        values = []
        for target_name in self.target_names:
            values.append(target_name)

        outputs = []
        outputs.append({
            "name": "Class",
            "size": len(self.target_names),
            "activation": "softmax",
            "use_bias": True,
            "values": values
        })

        return outputs
