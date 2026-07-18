"""
This module contains a sample experiment using ESP
"""
import os
import random

from esp_sdk.esp_evaluator import EspEvaluator
from esp_sdk.esp_service import EspService


_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT_DIR = os.path.join(_SCRIPT_DIR, '..', '..')

EXPERIMENT_PARAMS_FILE = os.path.join(_SCRIPT_DIR, 'experiment_params.hocon')


class ExampleValuator(EspEvaluator):
    def evaluate_candidate(self, candidate: object) -> dict:
        return {
            'score': random.randint(1, 10)
        }


def do_main():
    # Check for presence of credentials
    esp_username = os.getenv('AUTH0_USERNAME')
    esp_password = os.getenv('AUTH0_PASSWORD')
    if not esp_username or not esp_password:
        esp_username = os.getenv('ENN_USERNAME')
        esp_password = os.getenv('ENN_PASSWORD')
        if not esp_username or not esp_password:
            print('Please set environment AUTH0_USERNAME and AUTH0_PASSWORD variables before proceeding.')
    else:
        print('ESP Service username and password found.')

    experiment_params = EspService.load_experiment_params(EXPERIMENT_PARAMS_FILE)
    experiment_id = f'EspExample_{random.randint(1, 1000000):07}'
    experiment_params['LEAF']['experiment_id'] = experiment_id
    esp_service = EspService(experiment_params, esp_username, esp_password)
    evaluator = ExampleValuator(experiment_params)
    persistence_dir = esp_service.train(evaluator)
    print(f'Results written to {persistence_dir}')


if __name__ == '__main__':
    do_main()
