
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
import io
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
from _signal import SIGTERM
from fcntl import fcntl, F_SETFL, F_GETFL
from time import sleep
from unittest import TestCase

import grpc
from google.protobuf.json_format import ParseDict

from leaf_common.session.extension_packaging import ExtensionPackaging

from esp_service.grpc.python.generated.population_structs_pb2 import ExistingPopulationRequest
from esp_service.grpc.python.generated.population_structs_pb2 import PopulationRequest

from evolution_server.python.generated.population_service_pb2_grpc import PopulationServiceStub
from evolution_server.python.generated.system_info_service_pb2 import SystemInfoRequest
from evolution_server.python.generated.system_info_service_pb2_grpc import SystemInfoServiceStub

EXPERIMENT_ID = 'abcd1234'

ESP_HOST = 'localhost'

_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT_DIR = os.path.join(_ROOT_DIR, '../../..')
_ESP_SERVICE_DIR = os.path.join(_ROOT_DIR, '../..', 'python/esp')
_FIXTURES_PATH = os.path.join(_PROJECT_ROOT_DIR, 'tests/persistence/fixtures')
EXPERIMENT_PARAMS_FILE = os.path.join(_FIXTURES_PATH, 'evo_model.json')

CANDIDATE_SCORES = {
    '1_1': 1,
    '1_2': 2,
    '1_3': 3,
    '1_4': 4
}


class EspIntegrationTest(TestCase):
    """
    Very basic roundtrip integration test for ESPServer.

    We fire up an external instance of the server, ask for a seed population, fake-evaluate the population, then ask
    the ESP Server for the next generation. We also verify metrics were updated for the previous generation.
    """
    def setUp(self):
        self._grpc_port = self._get_free_tcp_port()
        esp_server_path = os.path.join(_ESP_SERVICE_DIR, 'esp_server.py')

        self._persist_dir = tempfile.mkdtemp()

        # Launch ESP subprocess in the background, using same virtualenv we are in and passing along our env vars.
        self._process = subprocess.Popen(
            [
                sys.executable,
                esp_server_path,
                '--port={}'.format(self._grpc_port),
                '--local-dir={}'.format(self._persist_dir),
            ],
            env={'PYTHONPATH': _PROJECT_ROOT_DIR, **os.environ},
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        self._stdout = self._process.stdout
        self._stderr = self._process.stderr

        self._set_stdout_nonblocking()

        self._extension_packaging = ExtensionPackaging()
        with open(EXPERIMENT_PARAMS_FILE) as f:
            self._experiment_params = json.load(f)

        # Use NNWeights format (faster)
        self._experiment_params['LEAF'] = {}
        self._experiment_params['LEAF']['representation'] = 'NNWeights'

        self._experiment_id = 'abc1234'

        channel = grpc.insecure_channel('{}:{}'.format(ESP_HOST, self._grpc_port))
        self._esp_service_stub = PopulationServiceStub(channel)
        self._system_info_stub = SystemInfoServiceStub(channel)
        self._wait_for_server_start()

        self._tests_passed = False

    def tearDown(self):
        if not self._tests_passed:
            print('Test(s) failed. stdout and stderr from spawned process:\n')
            with io.TextIOWrapper(self._stdout, encoding="utf-8") as f:
                for line in f:
                    print(line.rstrip())
            print('--- end of stdout and stderr ---')

        self._stdout.close()

        # clean up our temp dir
        shutil.rmtree(self._persist_dir)

        # kill spawned ESP server process
        self._process.send_signal(SIGTERM)
        exit_code = self._process.wait(30)
        if exit_code != 0 and exit_code != -SIGTERM:
            self.fail("Error killing esp_server process. Exit code: {}".format(exit_code))

    def test_evolve_generation(self):
        request_params = {
            'version': '1.0',
            'experiment_id': EXPERIMENT_ID
        }

        # get seed generation
        request = ParseDict(request_params, PopulationRequest())
        request.config = self._extension_packaging.to_extension_bytes(self._experiment_params)

        seed_response = self._esp_service_stub.NextPopulation(request)
        self.assertIsNotNone(seed_response)
        self.assertEqual(4, len(seed_response.population))

        # simulate evaluating candidates by requesting next generation
        self._evaluate_population(seed_response)
        request.evaluated_population_response.CopyFrom(seed_response)
        gen_2_response = self._esp_service_stub.NextPopulation(request)

        # assert new checkpoint ID
        self.assertNotEqual(seed_response.checkpoint_id, gen_2_response.checkpoint_id)

        # verify only best scored candidate survived
        seed_candidates = [candidate.id for candidate in seed_response.population]
        gen_2_candidates = [candidate.id for candidate in gen_2_response.population]

        # next generation should not be same candidates as previous generation
        self.assertNotEqual(seed_candidates, gen_2_candidates)

        common_candidates = set(seed_candidates) & set(gen_2_candidates)
        self.assertEqual(1, len(common_candidates))

        # we know there's only one so grab it and make sure it's the one we expect
        common_candidates_id = next(iter(common_candidates))
        self.assertEqual('1_4', common_candidates_id)

        # verify generation 1 (seed) metrics have been updated on the server:
        # gen 1 evaluation metrics are returned as "evaluation_stats" of gen 2.
        request_params = {
            'version': '1.0',
            'experiment_id': EXPERIMENT_ID,
            'checkpoint_id': gen_2_response.checkpoint_id
        }
        request = ParseDict(request_params, ExistingPopulationRequest())
        retrieved_population_response = self._esp_service_stub.GetPopulation(request)
        previous_gen_evaluation_stats = self._extension_packaging.from_extension_bytes(
            retrieved_population_response.evaluation_stats)
        previous_gen_metrics = previous_gen_evaluation_stats["server_metrics"]
        for candidate in seed_response.population:
            metrics = previous_gen_metrics[candidate.id]
            expected_score = CANDIDATE_SCORES[candidate.id]
            self.assertEqual(expected_score, metrics['score'])

        self._tests_passed = True

    @staticmethod
    def _evaluate_population(response):
        for candidate in response.population:
            # Update the metrics of the candidate
            # Create a json string. ESP expects a 'score' metric.
            metrics_json = json.dumps({"score": CANDIDATE_SCORES[candidate.id]})
            # and encode it in UTF-8 bytes
            candidate.metrics = metrics_json.encode('UTF-8')

    @staticmethod
    def _get_free_tcp_port():
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp.bind(('', 0))
        addr, port = tcp.getsockname()
        tcp.close()
        return port

    def _wait_for_server_start(self):
        max_attempts = 10
        sleep_time = 2
        attempt = 1
        while attempt < max_attempts:
            try:
                self._system_info_stub.GetSystemInfo(SystemInfoRequest())
                return
            except Exception:
                attempt += 1
                sleep(sleep_time)

        self.fail('Unable to confirm server start-up after {} seconds'.format(max_attempts * sleep_time))

    def _set_stdout_nonblocking(self):
        """
        Sets stdout of our spawned process to non-blocking. By default in Python stdout & stderr are blocking,
        so they would hang when we attempt to read.
        """
        flags = fcntl(self._stdout, F_GETFL)  # get current p.stdout flags
        fcntl(self._stdout, F_SETFL, flags | os.O_NONBLOCK)
