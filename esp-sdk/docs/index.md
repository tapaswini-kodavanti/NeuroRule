# Welcome to ESP SDK

The page contains the ESP SDK documentation.

# Windows installation

__Note__ All commands are to be executed in the Anaconda Prompt Terminal, not Windows Terminal.

## Anaconda
Install the newest version of Anaconda under your __user profile.__ To install Anaconda under your user profile make sure that during the installation the option 'install for this user only' is selected, not for all users on the computer. GSD is not familiar with this instructions so you have to actively guide them during the installation.

If you already have Anaconda installed on your system update conda to the latest version using:
```bash
(base) conda update -n base -c defaults conda
```

## Virtualenv
It is best to work in a separate environment for each project to prevent library errors and keep your other projects untouched. Create a new environment using the follow steps:
```bash
(base) conda create --name esp python=3.6.9
```
Check the environment is created correctly with:
```bash
(base) conda info --envs
```

## Git Clone
Activate the environment and install Git
```bash
(base) activate esp
(esp) conda install -c anaconda git
```

Navigate to your project directory (e.g. `LEAF` in the following instructions). Change your local directory path
 accordingly.
```bash
(esp) cd C:\Users\User\LEAF
```

Clone the git repo
```bash
(esp) git clone https://code.cognizant.com/leaf-ai/esp-demo.git
``` 

## Dependencies
Navigate to the cloned repo
```bash
(esp) cd esp-demo
```

Install dependencies.
```bash
(esp) pip install -r requirements.txt
```

When prompted for a git username and password, enter them. Note when entering a password in a terminal
 window you do not see yourself typing. This is a security feature. Just the type the password blind and hit enter.

```bash
Username for 'https://github.com': <type username here>
Password for 'https://github.com': <type passowrd here>
```

# MacOS installation

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

## Python 3.7.2
Install python 3.7.2:
```bash
pyenv install 3.7.2
```
If you run into a "zlib not available" error with Mojave, install the command line tools AND the headers:
```bash
xcode-select --install
sudo installer -pkg /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg -target /
```

([source](https://stackoverflow.com/questions/50036091/pyenv-zlib-error-on-macos))

## Git clone

Navigate to your project directory (e.g. `LEAF` in the following instructions):
```bash
cd $HOME/LEAF
```

Clone the git `esp-demo` repos:
```bash
git clone https://code.cognizant.com/leaf-ai/esp-demo.git
```

Navigate to the `esp-demo` directory you've just cloned
```bash
cd $HOME/LEAF/esp-demo
```

## Virtualenv
Create a virtual env
```bash
$HOME/.pyenv/versions/3.7.2/bin/python -m venv ./venv
```
Use it and set the python path:
```bash
source venv/bin/activate && export PYTHONPATH=`pwd`
```

## Dependencies
Install the required dependencies
```bash
pip install -r requirements.txt --upgrade
```

When prompted for a git username and password enter the following. Note when entering a password in a terminal window you do not see yourself typing. This is a security feature. Just the type the password blind and hit enter.

```bash
Username for 'https://github.com': <type username here>
Password for 'https://github.com': <type password here>
```

# Ubuntu 14.04 and 18.04 installation

## Pyenv

Prerequisites:
```bash
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python-openssl git
```

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

## Python 3.6.8
Python 3.7 does not work with Ubuntu 14.04 because it requires OpenSSL >=1.0.2 
Install python 3.6.8 instead with --enable-shared:
```bash
env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.6.8
```

## Virtualenv
Create a virtual env
```bash
$HOME/.pyenv/versions/3.6.8/bin/python -m venv ./venv
```
Use it and set the python path:
```bash
source venv/bin/activate && export PYTHONPATH=`pwd`
```

## Dependencies
Install the required dependencies
```bash
pip install -r requirements.txt
```

# Training

```python
# Instantiate the ESP service
esp_service = EspService(experiment_params)

# The XDE evaluator
my_evaluator = ... # your implementation of the EspNNWeightsEvaluator base class

# Start training!
persistence_dir = esp_service.train(my_evaluator)
```

# Checkpoints

To re-start an experiment from a checkpoint id, run:

```python
checkpoint_id = "..." # A checkpoint id received from the ESP service, as a string
persistence_dir = esp_service.train(my_evaluator, checkpoint_id=checkpoint_id)
```

# Documentation of experiment parameters
To view the documentation website with details regarding the experiment parameters,
navigate to the esp-sdk directory and run the **mkdocs serve** command. This will expose
the documentation on your local machine in a web browser. Your exact steps may vary
based on OS and directory structure. For example:

```console
(venv) ~/esp-demo$ pwd
/Users/leaf/esp-demo
(venv) ~/esp-demo$ cd ../esp-sdk
(venv) ~/esp-sdk$ mkdocs serve
INFO    -  Building documentation... 
INFO    -  Cleaning site directory 
INFO    -  Documentation built in 0.14 seconds 
[I 201028 15:33:21 server:335] Serving on http://127.0.0.1:8000
INFO    -  Serving on http://127.0.0.1:8000
```

Leave that command window running, then access the website by navigating
in a local web browser to http://127.0.0.1:8000

# Support

Connect with the LEAF ESP Community on [Yammer](https://www.yammer.com/cognizant.com/#/threads/inGroup?type=in_group&feedId=17402454&view=all).
