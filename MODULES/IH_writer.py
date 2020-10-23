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
	#TODO:
	# - mettre dans un try ? 
	# - ajouter résultats dans LOGS
	# - exporter les logs (+ settings ?), soit avec 2 types si même index, soit 2 index

	#pass
	#SETTINGS["OT_input"]["output"]=



	separator="/"
	server= "http://192.168.0.16:9200"
	mode= "post"
	index= "pas_output"
	document= "test_output"

	for to_output in SETTINGS["OT_input"]["output"]:
		es = Elasticsearch(server)
		data = [
			{
				"_index": index,
				"doc": json.dumps(handling, indent=4, default=str)
			} for handling in HANDLINGS
		]
		helpers.bulk(es, data)

	#ORIGINAL
	# for to_output in SETTINGS["OT_input"]["output"]:
	# 	es = Elasticsearch(to_output["options"][0]["value"])
	# 	data = [{
	# 		"_index": to_output["options"][1]["value"],
	# 		"doc": json.dumps(datum, indent=4, default=str)
	# 	} for datum in HANDLINGS]
	# 	helpers.bulk(es, data)


	#CLOTURE
	#	CLEANING
	#	LOGS
	return (HANDLINGS, PORT, LOGS )


#================================================================
