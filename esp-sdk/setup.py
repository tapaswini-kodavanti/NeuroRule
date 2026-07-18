"""
Code to allow this package to be pip-installed
"""
import os
import shutil
import subprocess
import sys

from importlib import metadata
from pathlib import Path
from setuptools import find_packages
from setuptools import setup

# Dependencies to package with ESP SDK
LEAF_COMMON_VERSION = "1.2.18"
PYLEAFAI_VERSION = "1.1.4"
# Note: ESP service is built by the evolution-service repo
ESP_SERVICE_VERSION = "3.3.3"

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 10)

if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write(f"""
==========================
Unsupported Python version
==========================
This version of esp-sdk requires Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}, but you're trying to
install it on Python {CURRENT_PYTHON[0]}.{CURRENT_PYTHON[1]}.
""")
    sys.exit(1)

# Temporary folders
TEMP_DIR = Path("temp")
TEMP_PACKAGES_DIR = TEMP_DIR / "packages"
# Unileaf bucket environment variable. Set in Codefresh.
UNILEAF_WHEEL_BUCKET_ENV_VAR = "UNILEAF_WHEEL_BUCKET"
DEFAULT_WHEEL_BUCKET = "leaf-unileaf-wheels"
# Private dependencies
LEAF_COMMON = "leaf_common"
PYLEAFAI = "pyleafai"
ESP_SERVICE = "esp_service"

# Make sure the build starts from a fresh, empty directory
if os.path.exists(TEMP_DIR):
    print(f"Cleaning up {TEMP_DIR} folder. Probably a left over of a previous failed build")
    shutil.rmtree(TEMP_DIR)

# Find where packages are installed by the setup process
distribution = metadata.distribution("setuptools")
# Get the path to that folder
PACKAGE_RESOURCE_PATH = Path(distribution.locate_file(''))
print(f"{PACKAGE_RESOURCE_PATH=}")


def download_file_from_s3(bucket_name, object_key, local_file_path):
    """
    Download private dependencies from S3
    Parameters
    ----------
    bucket_name The S3 bucket containing private dependencies
    object_key The full name of the dependency to download
    local_file_path The path where you want to save the downloaded file on the local machine

    Returns Nothing
    -------

    """
    # Create an S3 client. At that time we've checked boto3 has been installed
    # pylint: disable=import-outside-toplevel,import-error,broad-exception-caught
    import boto3
    s3 = boto3.client('s3')
    try:
        # Download the file from S3
        s3.download_file(bucket_name, object_key, local_file_path)
        print(f"File downloaded successfully to {local_file_path}")
    except Exception as e:
        print(f"Error downloading file: {e}")


def install_private_dependencies(bucket_name: str):
    """
    Downloads private dependencies from S3
    Parameters
    ----------
    bucket_name The S3 bucket containing the private dependencies wheel files

    Returns Nothing: dependencies get saved in the TEMP folder
    -------

    """

    # LEAF common
    s3_leaf_common_wheel_file = f"leaf_common/leaf_common-{LEAF_COMMON_VERSION}-py3-none-any.whl"
    local_leaf_common_wheel_file = TEMP_DIR / f"leaf_common-{LEAF_COMMON_VERSION}-py3-none-any.whl"
    # Download the dependency
    download_file_from_s3(bucket_name, s3_leaf_common_wheel_file, local_leaf_common_wheel_file)
    # Install it
    print(f"Installing {local_leaf_common_wheel_file} at {sys.executable}")
    subprocess.run([sys.executable, '-m', 'pip', 'install', local_leaf_common_wheel_file], check=True)

    # Pyleafai
    s3_pyleafai_wheel_file = f"pyleafai/pyleafai-{PYLEAFAI_VERSION}-py3-none-any.whl"
    local_pyleafai_wheel_file = TEMP_DIR / f"pyleafai-{PYLEAFAI_VERSION}-py3-none-any.whl"
    # Download the dependency
    download_file_from_s3(bucket_name, s3_pyleafai_wheel_file, local_pyleafai_wheel_file)
    # Install it
    print(f"Installing {local_pyleafai_wheel_file} at {sys.executable}")
    subprocess.run([sys.executable, '-m', 'pip', 'install', local_pyleafai_wheel_file], check=True)

    # ESP Service
    s3_esp_service_wheel_file = f"esp_service/esp_service-{ESP_SERVICE_VERSION}-py3-none-any.whl"
    local_esp_service_wheel_file = TEMP_DIR / f"esp_service-{ESP_SERVICE_VERSION}-py3-none-any.whl"
    # Download the dependency
    download_file_from_s3(bucket_name, s3_esp_service_wheel_file, local_esp_service_wheel_file)
    # Install it
    print(f"Installing {local_esp_service_wheel_file} at {sys.executable}")
    subprocess.run([sys.executable, '-m', 'pip', 'install', local_esp_service_wheel_file], check=True)

    # remove the boto3 whcih is not required further, to avoid interference with esp-sdk dependencies
    subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y', 'boto3'], check=True)


def prepare_package_dir():
    """
    Copies the code that needs to be packaged into a temporary folder.
    We have 2 ways of packaging `esp-sdk`:
    1. For developers that have access to the leaf-ai GitHub repos, we only need to package the code in the
     `esp_sdk` folder.
     This is the path used when running:
      `pip install git+https://${LEAF_SOURCE_CREDENTIALS}@github.com/leaf-ai/esp-sdk.git@4.0.6`
    2. For users that don't have access to the leaf-ai GitHub repos, we need to package the code in the `esp_sdk` folder
     AND the code from the private libraries (e.g. leaf_common, pyleafai, esp_service). The private libraries are
      downloaded from S3 as wheel files.
     This is the path used by Codefresh when building and exporting the `esp-sdk` wheel file.
    :return: the package_dir dictionary pointing to the folder containing the code to package
    """
    # Always include esp-sdk code
    # Create a temporary directory to contain the packages
    TEMP_PACKAGES_DIR.mkdir(parents=True, exist_ok=True)

    # Copy the esp_sdk folder in the temporary packages directory
    shutil.copytree("esp_sdk", TEMP_PACKAGES_DIR / "esp_sdk", dirs_exist_ok=True)

    # If exporting a wheel file, bundle private dependencies too
    # First, check if boto3 is installed
    try:
        # This method gets called twice when building the wheel file.
        # Check boto3 has been installed before starting the packaging
        # Boto3 is installed when packaging because it's in the setup_requires list
        # pylint: disable=import-outside-toplevel,unused-import
        import boto3  # noqa: F401 'boto3' imported but unused
    except ImportError:
        # boto3, required in setup_requires, has not been installed. Skip private dependencies.
        print("boto3 has not been installed. Skipping private dependencies bundling step")
        return {'': str(TEMP_PACKAGES_DIR)}

    # boto3 is installed.
    # Now check S3 credentials
    if boto3.session.Session().get_credentials() is None:
        # No S3 credentials. Skip private dependencies.
        print("No S3 credentials. Skipping private dependencies bundling step")
        return {'': str(TEMP_PACKAGES_DIR)}

    # Check whether an S3 bucket containing unileaf wheels has been specified
    bucket_name = os.environ.get(UNILEAF_WHEEL_BUCKET_ENV_VAR)
    if bucket_name is not None:
        print(f'Using S3 bucket defined by {UNILEAF_WHEEL_BUCKET_ENV_VAR}: {bucket_name}')
    else:
        # No S3 bucket. Skip private dependencies.
        print("No S3 bucket defined to access private dependencies wheels file."
              " Skipping private dependencies bundling step.")
        print(f"If you're trying to build an exportable wheel file that includes all the private dependencies required"
              f"by esp-sdk, set the UNILEAF_WHEEL_BUCKET environment variable, for instance to {DEFAULT_WHEEL_BUCKET},"
              f" and make sure the provided S3 credentials have access to it.")
        return {'': str(TEMP_PACKAGES_DIR)}

    # All good, private dependencies can be downloaded from S3.
    # Install them
    print("Installing private dependencies from wheels in S3")
    install_private_dependencies(bucket_name)

    # Package ESP service
    # First, package leaf_common (installed by esp_service during the setup_requires step)
    print(f"Looking for {LEAF_COMMON} at {PACKAGE_RESOURCE_PATH}")
    if os.path.exists(PACKAGE_RESOURCE_PATH / LEAF_COMMON):
        shutil.copytree(PACKAGE_RESOURCE_PATH / LEAF_COMMON, TEMP_PACKAGES_DIR / LEAF_COMMON, dirs_exist_ok=True)
        print(f"{LEAF_COMMON} copied to {TEMP_PACKAGES_DIR}")
    else:
        print(f"{LEAF_COMMON} unavailable at {PACKAGE_RESOURCE_PATH}")

    # Then, package pyleafai (installed by esp_service during the setup_requires step)
    print(f"Looking for {PYLEAFAI} at {PACKAGE_RESOURCE_PATH}")
    if os.path.exists(PACKAGE_RESOURCE_PATH / PYLEAFAI):
        shutil.copytree(PACKAGE_RESOURCE_PATH / PYLEAFAI, TEMP_PACKAGES_DIR / PYLEAFAI, dirs_exist_ok=True)
        print(f"{PYLEAFAI} copied to {TEMP_PACKAGES_DIR}")
    else:
        print(f"{PYLEAFAI} unavailable at {PACKAGE_RESOURCE_PATH}")

    # And finally esp_service itself
    print(f"Looking for {ESP_SERVICE} and schema at {PACKAGE_RESOURCE_PATH}")
    if os.path.exists(PACKAGE_RESOURCE_PATH / ESP_SERVICE):
        shutil.copytree(PACKAGE_RESOURCE_PATH / ESP_SERVICE, TEMP_PACKAGES_DIR / ESP_SERVICE, dirs_exist_ok=True)
        print(f"{ESP_SERVICE} copied to {TEMP_PACKAGES_DIR}")
        # Also copy the json schema, which is NOT copied with the packages because it's a data file
        # For reference, the levels are lib/python3.11/site-packages
        shutil.copytree(PACKAGE_RESOURCE_PATH / ESP_SERVICE / "schema",
                        TEMP_PACKAGES_DIR / ESP_SERVICE / "schema", dirs_exist_ok=True)
        print(f"schema copied to {TEMP_PACKAGES_DIR}")
    else:
        print(f"{ESP_SERVICE} and schema unavailable at {PACKAGE_RESOURCE_PATH}")

    return {'': str(TEMP_PACKAGES_DIR)}


def prepare_data_files():
    """
    Returns the list of data files to include.
    -------

    """
    data_files = [('', ['NOTICE.txt']),  # '' means this package,
                  ('', ['LICENSE.txt'])]
    # If ESP service has been bundled, also add the schema.json data file
    if os.path.exists(TEMP_PACKAGES_DIR / ESP_SERVICE):
        data_files.append(('esp_service/schema', ['temp/packages/esp_service/schema/experiment_params_schema.json']))
    return data_files


def read(fname):
    """
    Read file contents into a string
    :param fname: File to be read
    :return: String containing contents of file
    """
    with open(os.path.join(os.path.dirname(__file__), fname), encoding="utf-8") as file:
        return file.read()


setup(
    name='esp-sdk',

    # For versioning via scm (git) tag
    # See: https://pypi.org/project/setuptools-scm/
    use_scm_version=True,
    setup_requires=[
        'setuptools_scm',
        'boto3',
        'pip',
        # Internal dependency esp_service will be manually installed from a wheel file downloaded from S3.
    ],

    # Required version of Python
    python_requires=f'>={REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}',

    # Find the packages to included
    # packages=find_packages(where='.',  exclude=['tests*']),
    package_dir=prepare_package_dir(),
    packages=find_packages(where='./temp/packages', exclude=['esp_sdk.tests']),

    # Dependencies
    install_requires=[
        # Note: private dependencies, like leaf_common, are packaged with this repo's source code
        # But we still need to install their dependencies

        # leaf-common dependencies
        # Specifically use >= to specify a base version we know works
        # while allowing code that depends on this library to upgrade
        # versions as they see fit.
        "Deprecated>=1.2.14",
        # "grpcio>=1.62.0",  # ESP SDK uses a greater version
        "hvac>=1.1.0",
        "pyhocon>=0.3.60",
        "pyOpenSSL>=24.0.0",
        "PyJWT>=2.9.0",
        "pytz>=2023.1",
        "ruamel.yaml>=0.18.6",

        # ESP service dependencies
        'jsonschema>=4.21.1',

        # ESP SDK requirements
        'keras==3.8.0',
        'tensorflow==2.16.1',
        'h5py>=3.10.0',
        'numpy>=1.26.4',
        'tenacity==8.2.3',
        'pandas>=1.5.3',
        'matplotlib==3.8.3',

        'pathos==0.3.2',

        # leaf-common pulls this in as well, but with a >= specification
        'grpcio>=1.62.0',
        'protobuf>=4.25.3',

        # Transient dependency from esp-sdk's usage of pathos for multiprocessing
        # whose recent (5/20/2022) versions have caused trouble with leaf-distributed
        # unpacking of worker code.
        "ppft==1.7.6.8",
    ],
    # Add licensing info
    # And add the ESP service schema to the esp_service package. It's used by the service code to validate requests.
    data_files=prepare_data_files(),
    include_package_data=True,
    description='These modules enable ESP developers to create and run ESP experiments.',
    long_description=read('README.md'),
    author='Olivier Francon',
    url='https://github.com/leaf-ai/esp-sdk/'
)

# Don't forget to clean up
# Delete the temporary folder
if os.path.exists(TEMP_DIR):
    print(f"Build done. Cleaning up {TEMP_DIR} folder.")
    shutil.rmtree(TEMP_DIR)
