import json
#from typing import Iterable
#import jsonschema


def local_inputs_loader(HANDLINGS, PORT, LOGS, SETTINGS, name):
	'''
	Load local files (handlings and port's parameters) to PAS modelling inputs (port's raw stopover and parameters set)
	'''
	#NB : la vérification de conformité vis à vis des schémas était initialement faite à l'import (cf le settings du module). Mais pour certains cas, il serait mieux de faire cela à l'étape de conversion.

	#INITIALISATION
	MODLOGS = [f"{name} initialisation"]
	# LOGS.append(f"{name} initialisation")

	#CHARGEMENT DES FICHIERS

		# HANDLINGS
	message, loaded_json = get(SETTINGS["modules_settings"][name]["Handlings"])
	LOGS.append(message)
	HANDLINGS = loaded_json

		# PARAMETRES DU PORT
	for parameter in SETTINGS["modules_settings"][name]["Port"] :
		message, loaded_json = get(parameter)
		LOGS.append(message)
		PORT.update({parameter["name"]:loaded_json})


	return (HANDLINGS, PORT, LOGS)

# %% UTILITIES
def get(target):
	loaded_json = {}
	try:
		with open(target["file_path"]) as file :
			loaded_json = json.load(file)
	except FileNotFoundError: 
		message = f"{target.get('name', 'undefined name')} loading issue: invalid path ({target.get('file_path', 'undefined endpoint')})"
	except ValueError: 
		message = f"{target.get('name', 'undefined name')} loading issue: invalid json"
	else:
		message = f"{target.get('name', 'undefined name')} succefully loaded"
	
	return message, loaded_json
