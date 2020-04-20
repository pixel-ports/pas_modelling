# import logging
# import json
# from typing import Iterable
# import jsonschema
from elasticsearch import Elasticsearch
from elasticsearch import helpers

# logger = logging.getLogger("IH_writer")
# mod_name = "IH_writer:"


# def IH_writer(OT_INPUT, HANDLINGS, PORT, MODSETTINGS, LOGS):
def process(HANDLINGS, PORT, LOGS, SETTINGS, name):
	'''
	#FIXME
	'''
	#INITIALISATION
	LOGS.append(f"===== {name} STARTS =====")


	#ECRITURE
	for to_output in SETTINGS["OT_input"]["output"]:
		es = Elasticsearch(to_output["options"][0]["value"])
		data = [{
			"_index": to_output["options"][1]["value"],
			"doc": datum
		} for datum in HANDLINGS]
		helpers.bulk(es, data)


	#CLOTURE
	LOGS.append(f"===== {name} ENDS =====")
	return (HANDLINGS, PORT, LOGS, SETTINGS)


#================================================================
