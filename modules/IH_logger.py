import logging
import json
from typing import Iterable
import jsonschema
from elasticsearch import Elasticsearch
from elasticsearch import helpers

logger = logging.getLogger("IH_logger")
mod_name = "IH_logger:"


def IH_logger(OT_INPUT, HANDLINGS, PORT, MODSETTINGS, LOGS):
    '''
    Converts IH request parameters to PAS modelling inputs (port's raw stopover and parameters set)
    '''
    # NB : la vérification de conformité vis à vis des schémas était initialement faite à l'import (cf le settings du module). Mais pour certains cas, il serait mieux de faire cela à l'étape de conversion.

    # INITIALISATION
    logger.info("IH_logger initialisation")
    MODLOGS = ["IH_logger initialisation"]

    for to_log in OT_INPUT["logging"]:
        es = Elasticsearch(to_log["options"][0]["value"])
        data = [{
            "_index": to_log["options"][1]["value"],
            "doc": {
                "body": str(datum)
            }
        } for datum in LOGS]
        helpers.bulk(es, data)

    return (HANDLINGS, PORT, MODLOGS)
