# PIXEL Port Activity Scenario Modelling

This repository implements the PAS modelling presented in the MTC paper : https://www.dropbox.com/s/6z2e854bxz9jtur/MTC2019_SIMON_LACALLE.pdf?dl=0.

## Getting started

On linux, run the following commands in order to get started :

```bash
sudo apt-get install python3 python3-dev
sudo pip install pipenv  # installs pipenv globally
pipenv install  # installs the required dependencies
git config core.hooksPath .githooks  # defines project git hooks folder
```
Then update files in `data/` according to your port needs or leave them as they are, then start the process :

```bash
pipenv run python main.py
```

You can add the the option `--step 1` if you want to run only the first step. Available steps are `1`, `2` and `3`.

## Generate fake data for demonstration

```bash
pipenv run python tools/fake_pas_generation.py
pipenv run jupyter-notebook tools/demonstration.ipynb
```

## Monitor memory/cpu usage

```bash
pipenv run mprof run test.py && pipenv run mprof plot # RAM
pipenv run python test/test_monitor_cpu.py  # CPU
```

## Changes from the paper

Here is what needs to be changed :
  - Change cargo property of cargo element, because it is redondant.
  - Add an id to the operations and check that those ids are unique
  - Check that ids are unique everywhere
  - Check that cargo category and type are coherent
  - Add the possibility to distribute work between concurrent operations/machines
  - Implement check rules that will be given by Erwan
  - Add throughput to manage multi-machine (but re-think about it with Erwan)
  - Integrate edition
  - Try an "automate" system
  - Add Area datamodel
  - Split code by steps
  - Create and document a Docker image

  - Remove all `.list` for a cleaner thing
  - Use Singleton Pattern
  - Unit Tests
  - Add black with auto-commit
  - Add a Machine type beneath MachineCollection for all sub-operations ? And do the same with all other types ?

Here is what has already been changed :
  - SetupTime is not set as a property but is part of the "FixedDelay" for an operation.
  - FixedDelay can receive a negative value