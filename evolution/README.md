# evolution
Using ESP service to create a simple evolutionary computation domain.

For evolving existing representations, you only need to implement an evaluator 
like ruleBaseEvaluator.py and create your desired metrics to calculate final fitness.

The concept of an environment for the data driven evaluation is yet to come.

For evolving a new representation, ([leaf-common](https://github.com/leaf-ai/leaf-common)) 
needs to be extended to have the definitions for the new representation.

 
Then ([evolution-service](https://github.com/leaf-ai/evolution-service)) 
should implement initialization, randomization and genetic operators.


Rule representation code on each side will be a good example to follow.    


# Setup (macOS)
## Homebrew
Install Homebrew:
```bash
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```
See [Homebrew's main page](https://brew.sh/) for more information.

## Pyenv
Install pyenv:
```bash
brew install pyenv
```

## Python 3.10
Install python 3.10 (note that the minor version doesn't matter much):
```bash
pyenv install 3.10
```

For mac:
If you run into a "zlib not available" error with Mojave, install the command line tools AND the headers:
```bash
xcode-select --install
sudo installer -pkg /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg -target /
```

([source](https://stackoverflow.com/questions/50036091/pyenv-zlib-error-on-macos))

## Virtualenv
Create a virtual env
```bash
pip install virtualenv
virtualenv --python=/usr/bin/python3.10 ~/venv/evolution-3.10
```
Use it:
```bash
source ~/venv/evolution-3.10/bin/activate
```

## $PYTHONPATH
Set up the python path.
This assumes that the other repos mentioned are peers to this one.
```bash
export PYTHONPATH=`pwd`/../leaf-common:`pwd`/../esp-sdk:`pwd`
```

If you want to do all-local evolution runs (without a separate service process),
you will need the evolution-service repo handy as well as its pip requirements:
```bash
export PYTHONPATH=`pwd`/../pyleafai:`pwd`/../leaf-common:`pwd`/../esp-sdk:`pwd`/../evolution-service:`pwd`
```

If you want to do distributed candidate evaluations
you will also need the deepbilevel repo handy as a peer repo *at the very end*:
```bash
export PYTHONPATH=`pwd`/../pyleafai:`pwd`/../leaf-common:`pwd`/../esp-sdk:`pwd`/../evolution-service:`pwd`:`pwd`/../deepbilevel
```
... and its repo pip requirements as well


## Dependencies
Install the required dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-build.txt
```

Set up the evolution service (if it is available)
```bash
cd ../evolution-service/
./esp_service/grpc/python/generate.sh
./evolution_server/python/generate.sh
```

## Troubleshooting
If you encounter this error when importing matplotlib
```commandline
ImportError: Python is not installed as a framework.
```

Add a file in your home directory
```commandline
~/.matplotlib/matplotlibrc
```
that contains
```commandline
backend: Agg
```

Full discussion is available here
https://stackoverflow.com/questions/47356726/fix-matplotlib-not-installed-as-framework-error-w-out-changing-matplotlib-con

# Setup (Ubuntu)
## Pyenv

Prerequisites:
```bash
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python-openssl git

sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python-setuptools python3.10 python3-dev python3.10-dev

Install pyenv:
```bash
curl https://pyenv.run | bash
```

Load pyenv automatically by adding
the following to ~/.bashrc:
```bash
export PATH="${HOME}/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

([source](https://github.com/pyenv/pyenv-installer))



## Domains
Some domains have extra instructutions to get their prerequisites installed.
See domain README.md files for details.

# Example Execution
From the top-level directory of this repo, using the PYTHONPATH set above ...
```bash
python app/evolve.py -p domain/vector_optimizer/numfind_params.hocon
```

Examples of running all-local with no extra service process:
```bash
python app/evolve.py -p domain/leading_one/leading_one_local.hocon
python app/evolve.py -p domain/nas_bench/nas_bench_local.hocon
python app/evolve.py -p domain/binary_string/leading_ones_local.hocon
```

An example of running distributed candidate evaluation:
```bash
python app/evolve.py -p domain/vector_optimizer/distributed_numfind.hocon
```

An example of running all-local ace with no extra service process:
```bash
python app/evolve.py -p domain/binary_string/leading_ones_ace_local.hocon
```
