# GitHub actions configuration

Informations for GitHub actions configuration

## Logic
On "Develop" branch:
- Tests involve pure python code (not the docker image). 
- In PAS_builder, the main try/except security sould be off (#FIXME, that's discusting!)
- Each push should at least pass a minimal test : (develop_minimal_test). 
- Each time a feature branch is merge on Develop, a feature specific test should be added and be pass by every futur push on Develop

## develop_minimal_test
Test if :
- dependencies are clear
- PAS_builder run without error on local PAS_instance (python3 ./PAS_builder.py --pipeline=local_PAS_instance, --OT_input=local_file)

## Dependencies:

argparse
json
sys
datetime
from elasticsearch import Elasticsearch
from elasticsearch import helpers
iterable*
jsonschema*
statistics*

*: oudated (legacy stuff that should be removed ?) #TODO
