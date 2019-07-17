# PIXEL Port Activity Scenario Modelling

This repository implements the PAS modelling presented in the MTC paper : https://www.dropbox.com/s/6z2e854bxz9jtur/MTC2019_SIMON_LACALLE.pdf?dl=0.

## Getting started

Update files in `data/` according to your port needs or leave them as they are, then start the process :

```bash
python main.py  # python3 or above
```

It generates a `pas.json` file containing the **Port Activity Scenario**.

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

Here is what has already been changed :
  - SetupTime is not set as a property but is part of the "FixedDelay" for an operation.
  - FixedDelay can receive a negative value