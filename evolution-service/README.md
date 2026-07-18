# Evolution service

This repository contains the Evolution Service.
It provides the `NextPopulation` and `GetPopulation` gRPC APIs
to the Evolution and ESP clients to evolve
population of different type of representations. 

This module relies on [Keras](https://keras.io/) for the neural network 
representation implementation.

# Setup

## Clone the repo
Assuming your code usually goes in `$HOME/workspace/`
```shell
cd $HOME/workspace
```

Clone the repo. Assuming you have an SSH key in GitHub:
```shell
git clone git@github.com:leaf-ai/evolution-service.git
```

```shell
cd evolution-service
```

## MacOS

### Homebrew
Install Homebrew:
```shell
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```
See [Homebrew's main page](https://brew.sh/) for more information.

### Pyenv
Install pyenv:
```shell
brew install pyenv
```

### Python 3.8.9
Install python 3.8.9:
```shell
pyenv install 3.8.9
```
If you run into a "zlib not available" error with Mojave, install the command line tools AND the headers:
```shell
xcode-select --install
sudo installer -pkg /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg -target /
```

([source](https://stackoverflow.com/questions/50036091/pyenv-zlib-error-on-macos))

### Virtualenv
Create a virtual env
```shell
$HOME/.pyenv/versions/3.8.9/bin/python -m venv $HOME/workspace/evolution-service/venv
```
Use it:
```shell
source $HOME/workspace/evolution-service/venv/bin/activate
```

### $PYTHONPATH
Set up the python path:
```shell
export PYTHONPATH=$HOME/workspace/evolution-service
```

### Dependencies
Install the required dependencies
```shell
pip install -r requirements.txt
``` 

## Ubuntu

### PyEnv

Install [PyEnv](https://github.com/pyenv/pyenv) to quickly have access to any Python version

#### Dependencies

According to [common build problems](https://github.com/pyenv/pyenv/wiki/common-build-problems) page,
make sure these packages are installed

```shell
sudo apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git
```

#### PyEnv installation
Install [PyEnv](https://github.com/pyenv/pyenv-installer):
```shell
curl https://pyenv.run | bash
```

As prompted, add pyenv to the load path. Add the following lines at the end of
your ~/.bashrc (or ~/.zshrc if using zsh):
```shell
export PATH="${HOME}/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Then restart your shell for the path changes take effect

### Python 3.8.9

Install Python 3.8.9 with [shared libraries](https://github.com/pyenv/pyenv/wiki#how-to-build-cpython-with---enable-shared)
 to avoid [linking issues](https://stackoverflow.com/questions/42582712/relocation-r-x86-64-32s-against-py-notimplementedstruct-can-not-be-used-when)
 with third party dependencies.
```shell
PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.10.13
```

### Virtualenv

Create a venv:
```shell
$HOME/.pyenv/versions/3.10.13/bin/python -m venv ./venv
```

Use it:
```shell
source $HOME/workspace/evolution-service/venv/bin/activate
```

### $PYTHONPATH
Set up the python path:
```shell
export PYTHONPATH=$HOME/workspace/evolution-service
```

### Dependencies
Install the required dependencies
```shell
pip install -r requirements.txt
``` 

### Locale

Set the locale to UTF-8

```shell
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

## Run the unit tests:
Generate the gRPC stubs:
```shell
$HOME/workspace/evolution-service/esp_service/grpc/python/generate.sh
$HOME/workspace/evolution-service/evolution_server/python/generate.sh
```
Run the tests. This will self-discover all the tests that are available to run.
```shell
pytest --verbose .
```
Useful other commands to run tests from 1 specific file only:
```shell
pytest --verbose tests/representations/nnweights/base_model/test_create_model.py
```
To run 1 single test:
```shell
pytest --verbose tests/representations/nnweights/base_model/test_create_model.py:TestModelCreation.test_create_model
```

## Flake8

flake8 and tests are run on [Codefresh](https://g.codefresh.io/pipelines)
 on every git push. To avoid failures, install flake8 pre-commit hook:
```shell
pip install flake8
flake8 --install-hook git
git config --bool flake8.strict true
```

(source: http://flake8.pycqa.org/en/latest/user/using-hooks.html)

# Evolution as a service

## Start the service

### With no persistence

To start the service locally with no persistence for the generated populations, i.e. no checkpointing:

```shell
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
python evolution_server/python/esp/esp_server.py
```

### With local persistence

To start the service locally with check-pointing, persisting population to a local folder:

```shell
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
python evolution_server/python/esp/esp_server.py --local-dir "/path/to/persistence/directory"
```

### With S3 persistence

To start the service locally with check-pointing, persisting population to S3:

```shell
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Make sure AWS credentials are available. For instance, by using these 2 env variables
export AWS_ACCESS_KEY_ID=XXXXXXXX
export AWS_SECRET_ACCESS_KEY=XXXXXXXX

python evolution_server/python/esp/esp_server.py --bucket esp-models
```

## Use the service as a library

It's also possible to use the service directly as a library,
skipping the gRPC layer, for developing or debugging for instance:

1. Add this repo to the `PYTHONPATH`
1. In the client config, set `esp_host` to `null` or `None`.

## Service APIs

See the gRPC proto files in [evolution_server/protos](evolution_server/protos), in particular [population_service.proto](evolution_server/protos/population_service.proto)
