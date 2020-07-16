# import logging
import json
# from typing import Iterable
# import jsonschema
from elasticsearch import Elasticsearch
from elasticsearch import helpers

# logger = logging.getLogger("IH_writer")
# mod_name = "IH_writer:"


# def IH_writer(OT_INPUT, HANDLINGS, PORT, MODSETTINGS, LOGS):
def main(HANDLINGS, PORT, LOGS, SETTINGS, module_name):
	'''
	Write all components of PAS_modelling's output (Logs, Settings, Inputs (handlings + port's parameters)) in Information Hub.
	NB: each PAS run produce a need index, with 
	'''
	#INITIALISATION
	LOGS.append(f"==== {module_name}  ====")


	#ECRITURE
	#FIXME format des ts exportable: Unable to serialize datetime.timedelta(
	#FIXME mettre dans un try ? + log

	for to_output in SETTINGS["OT_input"]["output"]:
		es = Elasticsearch(to_output["options"][0]["value"])
		data = [{
			"_index": to_output["options"][1]["value"],
			"doc": json.dumps(datum, indent=4, default=str)
		} for datum in HANDLINGS]
		helpers.bulk(es, data)


	#CLOTURE
	#	CLEANING
	#	LOGS
	return (HANDLINGS, PORT, LOGS, SETTINGS)


#================================================================