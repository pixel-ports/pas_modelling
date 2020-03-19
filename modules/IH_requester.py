import logging
import json
from typing import Iterable
import jsonschema
from elasticsearch import Elasticsearch

logger = logging.getLogger("IH_requester")
mod_name = "IH_requester:"

def IH_requester(OT_INPUT, HANDLINGS, PORT, MODSETTINGS, LOGS):
	'''
	Converts IH request parameters to PAS modelling inputs (port's raw stopover and parameters set)
	'''
	#NB : la vérification de conformité vis à vis des schémas était initialement faite à l'import (cf le settings du module). Mais pour certains cas, il serait mieux de faire cela à l'étape de conversion.

	#INITIALISATION
	logger.info("IH_requester initialisation")
	MODLOGS = ["IH_requester initialisation"]

	for name in ["supplychains", "rules", "resources"]:
		message, data = get(OT_INPUT, name)
		if message:
			MODLOGS.append(message)
		PORT.update({name: data})

	message, data = get(OT_INPUT, "pas-input")
	if message:
		MODLOGS.append(message)
	HANDLINGS = data

	return (HANDLINGS, PORT, MODLOGS)

# %% UTILITIES
def get(pas_instance_data, name):
	message = None
	data = None
	input_element = next(x for x in pas_instance_data["input"] if x["name"]==name)
	if input_element["category"] == "ih-api":
		es = Elasticsearch(input_element["options"][0]["value"])
		if len(input_element["options"]) == 2:  # We retrieve all data from index
			input_body = {
				"query": {
					"match_all": {}
				}
			}
		elif len(input_element["options"]) == 4:  # For the pas_input
			input_body = {  # TODO: Implement the fact that there can be multiple timeIntervals
				"query": {
					"range" : {
						"timestamp" : {
							"gte" : input_element["options"][2]["value"],
							"lte" : input_element["options"][3]["value"]
						}
					}
				}
			}
		else:
			raise Exception("Incorrect number of parameters in json input")
		index = input_element["options"][1]["value"]
		response = es.search(index=index, body={"query": {"match_all": {}}})
		data = [hit for hit in response["hits"]["hits"]]
	elif input_element["category"]=="forceInput":
		data = next(x["value"] for x in pas_instance_data["forceinput"] if x["name"]==name)
	else:
		message = "Unknown input_element category: %s" % input_element["category"]
	return message, data
