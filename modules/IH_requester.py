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
	Rêgle 1: ne pas crasher ==> encapsuler dans un try?
	Rêgle 2: renvoyer le PAS ==> on ajoute de l'info, ne pas remplacer par bloc logs par exemple
	Rêgle 3: on ronvera dans tout les cas des logs
	'''

	#INITIALISATION
	logger.warning("IH_requester initialisation")
	MODLOGS = ["IH_requester initialisation"]
	IH_CALLS = HANDLINGS.copy()


	#RECUPERATION DATA
	## HANDLINGS
	Handlings_request = [request 
		for request in IH_CALLS["input"] 
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

	##PORT
	Port_request = [request 
		for request in IH_CALLS["input"] 
		if request["type"] == "Port_parameters" #Attention, doit matcher avec l'IH!
	]
	if len(Port_request) == 0 : #On peut éventuellement ajouter une vérification plus rigoureuse
		MODLOGS.append(f"prb, aucun port's parameters dans le call à l'IH!")
	else:
		for request in Port_request :
			request_status, request_object = get(request)
			MODLOGS.append(request_status)
			PORT.update(request_object)
			
	# #Log d'entrée en service (status inputs)
	# #Récup fichiers
	# 	Liste des fichiers à récuperer
	# 	call de la fonction de récup
	# 	ajout aux log du message
	# 	ajout du fichier en PAs ? (avec un test avant ?)
	# #Log de sortie (status ouput (résumé ok et erreurs))


	# # RÉCUPÉRATIONS STOPOVERS #FIXME remplacer par la récupération des données de l'IH (recus dans PAS["HANDLINGS"])
	# HANDLINGS = <<mettre fonction pr get data [record["data"] for record in load(MODSETTINGS["handlings"]["full_path"], MODLOGS)[0]["records"]] #Le 0 est pr le terminal de Bassens
	# MODLOGS.append(f"{mod_name} IH's stopover successfully imported")
	

	# RÉCUPÉRATION DES PARAMÈTRES 
	# for parameter_name in MODSETTINGS["pas_parameters"]["name"] :
	#     # CHARGEMENT DU JSON #FIXME idem
	#     PARAMETERS[parameter_name] = load(
	#         MODSETTINGS["pas_parameters"]["folder_path"] + parameter_name + MODSETTINGS["pas_parameters"]["suffix"],
	#         MODLOGS
	#     )
	#     message = f"IH_requester: IH's parameter {parameter_name} successfully imported" ; MODLOGS.append(message) ; logger.warning(message)
		
	#     # CHARGEMENT DU SCHEMA
	#     schema_path = "toto" + MODSETTINGS["schemas"]["folder_path"] + parameter_name + MODSETTINGS["schemas"]["suffix"]
	#     try :
	#         with open(schema_path) as file :
	#             schema = json.load(file)
	#     except FileNotFoundError: 
	#         message = f"IH_requester: json-schema parameter {parameter_name} file not found in {schema_path}" ; MODLOGS.append(message) ; logger.warning(message)
	#     except ValueError: 
	#         message = f"IH_requester: json-schema parameter {parameter_name} can not be loaded (invalid json)" ; MODLOGS.append(message) ; logger.warning(message)
	#     else:
	#         message = f"IH_requester: json-schema parameter {parameter_name} succefully loaded" ; MODLOGS.append(message) ; logger.warning(message)    
		
	#     # CONFRONTATION JSON VS SCHEMA
	#     try:
	#         jsonschema.validate(
	#             PAS["parameters"][parameter_name], 
	#             schema
	#         )       
	#     except: #FIXME catch le message d'erreur décrivant l'invalidité et le passer dans les MODLOGS
	#         MODLOGS.append(f"IH_requester: {parameter_name} unvalid against shema")
	#         message = f"IH_requester: {parameter_name} unvalid against shema" ; MODLOGS.append(message) ; logger.warning(message)
	#     else :
	#         message = f"IH_requester: {parameter_name} successfully tested against shema" ; MODLOGS.append(message) ; logger.warning(message)
	
		

	# logger.warning("Ending")
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
