# PIXEL Port Activity Scenario Modelling
## Synopsis
This repository contains the PAS model. The purpose if to :
1. from vessel-calls and port-parameter, build the PAS ("what, when, how ?")
2. pass the PAS to a chain of outcome-modules for additional information, such as:
- energy consumption,
- pollutant emission,
- operators involved (future feature)
## Use 
To run it, run main.py though python 3 with inputs in the "--PAS_instance" argument. If no PAS_instance is provided, the ./DOCLERISATION/PAS_instance.json will be loaded.
Environment requirement are specified in ./DOCLERISATION/requirements.txt.
### Inputs
Generate port setting
Selection of settings
### Outputs
#### PAS
The PAS output provide for each vessel-call the list of activities in the dock to process it. Activities correspond to atomic operations described in supply-chains. Briefly, for each activity is provided:
- information (operation description),
- scheduling (start, duration, end),
- resources used (such as machines or buildings)
Furthermore, depending on outcome modules activated (settings), additional information can be added to each resource used, as :
- energy consumption (nature, quantity),
- pollutant emission (nature, quantity)
Those information can be aggregated (e.g. sum, mean etc) or normalized (e.g. quantity/ton).
...
#### Internal logs
...
## Current state
...
### Limitations
- cargo (déchargement ou chargement complet)
### Possible future features
- operator density
## Dockers image
The model can be use by itself (considering it receive a proper PAS_instance) but is mean to be deployed in PIXEL platform. This mean thought a Docker image. To build the image:

```bash
docker build -t pas_model .
docker run --env-file .env -v pas_model python3 main.py --PAS_instance {PAS instance content}
```
