import logging
import json
from typing import Iterable
import jsonschema
from pathlib import Path
import requests

logger = logging.getLogger("IH_requester")
mod_name = "IH_requester:"

def IH_requester(HANDLINGS, PORT, MODSETTINGS):
	'''
	Converts IH request parameters to PAS modelling inputs (port's raw stopover and parameters set)
	'''
	#NB : la vérification de conformité vis à vis des schémas était initialement faite à l'import (cf le settings du module). Mais pour certains cas, il serait mieux de faire cela à l'étape de conversion.

	#INITIALISATION
	logger.warning("IH_requester initialisation")
	MODLOGS = ["IH_requester initialisation"]

	for name in ["supplychains", "rules", "resources"]:
		message, data = get(HANDLINGS, name)
		if message:
			MODLOGS.append(message)
		PORT.update({name: data})

	message, data = get(HANDLINGS, "pas-input")
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
		input_body = {
			"source": {
				"sourceId": input_element["options"][2]["value"]
			}
		}
		if len(input_element["options"]) > 3:  # For the pas_input
			input_body["timeIntervals"] = [  # TODO: Implement the fact that there can be multiple timeIntervals
				{
					"start": input_element["options"][3]["value"],
					"end": input_element["options"][4]["value"]
				}
			]
		url = input_element["options"][0]["value"] + input_element["options"][1]["value"]
		response = requests.post(
			url,
			headers = {
				'Content-Type': 'application/json',
				'Accept': 'application/json'
			},
			data=input_body
		)
		data = response.json()
	elif input_element["category"]=="forceInput":
		data = next(x["value"] for x in pas_instance_data["forceinput"] if x["name"]==name)
	else:
		message = "Unknown input_element category: %s" % input_element["category"]
	return message, data
