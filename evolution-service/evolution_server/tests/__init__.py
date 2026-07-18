'''
The code in this file gets executed before any of the tests are run. It is used for setting up the test environment.
'''
import os

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_DIR = os.path.join(SRC_DIR, '../..')
PROTO_DIR = os.path.join(PROJECT_ROOT_DIR, 'evolution_server/protos')
GENERATED_FILES_DIR = os.path.join(PROJECT_ROOT_DIR, 'evolution_server/python/generated')


def setup_package():
    # Check if proto file is newer than gRPC stubs, meaning we should regenerate the stubs.

    newest_proto_timestamp = None
    for filename in os.listdir(PROTO_DIR):
        # only interested in protobuff files, not other random junk
        if not filename.endswith('.proto'):
            continue

        full_path = os.path.join(PROTO_DIR, filename)
        proto_file_timestamp = os.path.getmtime(full_path)
        if not newest_proto_timestamp or proto_file_timestamp > newest_proto_timestamp:
            newest_proto_timestamp = proto_file_timestamp

    oldest_gen_file_timestamp = None
    for filename in os.listdir(GENERATED_FILES_DIR):
        # only interested in Python files, not other random junk
        if not filename.endswith('.py'):
            continue

        full_path = os.path.join(GENERATED_FILES_DIR, filename)
        gen_file_timestamp = os.path.getmtime(full_path)
        if not oldest_gen_file_timestamp or gen_file_timestamp < oldest_gen_file_timestamp:
            oldest_gen_file_timestamp = gen_file_timestamp

    # check if we need to regen gRPC files
    if newest_proto_timestamp > oldest_gen_file_timestamp:
        print('Generated gRPC stubs are out of date. Regenerating...')
        ret_val = os.system(os.path.join(PROJECT_ROOT_DIR, 'esp_service/grpc/python/generate.sh'))
        ret_val = os.system(os.path.join(PROJECT_ROOT_DIR, 'evolution_server/python/generate.sh'))
        assert ret_val == 0
