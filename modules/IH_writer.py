import logging
import json
from typing import Iterable
import jsonschema
from elasticsearch import Elasticsearch
from elasticsearch import helpers

logger = logging.getLogger("IH_writer")
mod_name = "IH_writer:"


def IH_writer(OT_INPUT, HANDLINGS, PORT, MODSETTINGS, LOGS):
    '''
    Converts IH request parameters to PAS modelling inputs (port's raw stopover and parameters set)
    '''
    # NB : la vérification de conformité vis à vis des schémas était initialement faite à l'import (cf le settings du module). Mais pour certains cas, il serait mieux de faire cela à l'étape de conversion.

    # INITIALISATION
    logger.info("IH_logger initialisation")
    MODLOGS = ["IH_logger initialisation"]

    for to_output in OT_INPUT["output"]:
        es = Elasticsearch(to_output["options"][0]["value"])
        data = [{
            "_index": to_output["options"][1]["value"],
            "doc": datum
        } for datum in HANDLINGS]
        helpers.bulk(es, data)

    return (HANDLINGS, PORT, MODLOGS)
