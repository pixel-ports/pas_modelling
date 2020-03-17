import logging
import json
from typing import Iterable
import jsonschema
from pathlib import Path

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


	#RECUPERATION DATA (EXTERIEURES)
	##PORT
	Port_request = [request 
		for request in HANDLINGS["input"] 
		if request["type"] == "Port_parameters" #Attention, doit matcher avec l'IH!
	]
	if len(Port_request) == 0 : #On peut éventuellement ajouter une vérification plus rigoureuse
		MODLOGS.append(f"prb, aucun port's parameters dans le call à l'IH!")
	else:
		for request in Port_request :
			request_status, request_object = get(request)
			MODLOGS.append(request_status)
			PORT.update({request["name"]:request_object})
	
	## HANDLINGS
	Handlings_request = [request 
		for request in HANDLINGS["input"] 
		if request["type"] == "Vessel_Calls" #Attention, doit matcher avec l'IH!
	]
	if len(Handlings_request) > 1:
		MODLOGS.append(f"prb, plus d'un handling dans le call à l'IH!")
	if len(Handlings_request) ==0 :
		MODLOGS.append(f"prb, aucun handling dans le call à l'IH!")
	else:
		request_status, request_object = get(Handlings_request[0])
		MODLOGS.append(request_status)
		HANDLINGS = request_object[0]["records"]


	return (HANDLINGS, PORT, MODLOGS)

# %% UTILITIES
def get(request):
	loaded_json = {}
	try:
		with open(request["endpoint"]) as file :
			loaded_json = json.load(file)
	except FileNotFoundError: 
		message = f"{request.get('name', 'undefined name')} loading issue: invalid source ({request.get('endpoint', 'undefined endpoint')})"		
	except ValueError: 
		message = f"{request.get('name', 'undefined name')} loading issue: invalid file"
	else:
		message = f"{request.get('name', 'undefined name')} succefully loaded"
	
	return message, loaded_json
