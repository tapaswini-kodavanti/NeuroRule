"""
See class comment.
"""

from typing import Dict
import numpy as np

from leaf_common.representation.rule_based.evaluation.rule_set_evaluator \
    import RuleSetEvaluator
from leaf_common.representation.rule_based.data import rule_set
from leaf_common.representation.rule_based.data.rules_constants \
    import RulesConstants


class RulesModel():
    """
    Code relating to evaluation of Rule_based prescriptor.
    It has been implemented to mitigate the high level of dependency our
    current domain has on Keras models
    """

    def __init__(self, candidate: rule_set, config: Dict[str, object]):
        self.candidate = candidate
        self.states, self.actions = self._get_states_and_actions(config)

    def predict(self, data):
        # This method instantiates only one evaluator object to run prediction
        # on the whole data table
        evaluator = RuleSetEvaluator(self.states, self.actions)
        predictions = []
        for i in range(len(data[0])):
            # We need the feature keys to create consumable data by evaluator
            data_dictionary = dict(self.states)
            # query the keys and replace data values on the feature names
            for key in data_dictionary:
                data_dictionary[key] = data[int(key)][i]
            actions_dict = \
                evaluator.choose_action(self.candidate, data_dictionary)
            actions = []
            # aggregate all the votes and co-efficients into the output vector
            for action_dict in actions_dict.values():
                if action_dict[RulesConstants.ACTION_COUNT_KEY] > 0:
                    actions.append(
                        (action_dict[RulesConstants.ACTION_COEFFICIENT_KEY] /
                         action_dict[RulesConstants.ACTION_COUNT_KEY]))
                else:
                    # if there is not vote for an action let's pad it with zero
                    actions.append(0.0)

            # A full size output vector with aggregated scores between 0 and 1
            predictions.append(actions)
        predictions = np.array(predictions)
        return predictions

    def _get_states_and_actions(self, config):
        states = self._read_config_shape_var(config['network']['inputs'])
        actions = self._read_config_shape_var(config['network']['outputs'])
        return states, actions

    def _read_config_shape_var(self, config_var):
        if config_var[0]['size'] > 1:
            shape_vars = {str(i): config_var[0]['name'] + '_' + str(i)
                          for i in range(config_var[0]['size'])}
        else:
            shape_vars = {str(i): config_var[i]['name']
                          for i in range(len(config_var))}
        
        return shape_vars

    def to_string(self):
        return self.candidate.to_string(
            states=self.states, actions=self.actions)
