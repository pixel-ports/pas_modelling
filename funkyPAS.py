# -*- coding: utf-8 -*-

import argparse
import json
import sys
sys.path.insert(0, "./modules")


def main(pipeline_name, OT_input) :
	'''
	Pour le pipeline passé en argument, appelle successivement les différents modules, leurs passant successivement l'objet "PAS" qui contient l'entièreté des données afférente au scénario.
	'''
	# INITIALISATION
	HANDLINGS = [] #Liste des vessel calls à traiter
	PORT = {} #Conteneur pour l'ensemble des paramètres décrivant le port
	LOGS = [f"Starting PAS modelling: {pipeline_name}"] #Array pr fils chronologique
	#	OT_input
	if OT_input == "local_file": 
		with open("./IH_testing/PAS_instance (CHR) extention SC.json") as file :
			OT_input = json.load(file)
		LOGS.append(f"Loading OT_input from file {file}: Success") 
	else :
		try:
			#On convertie la string recue en dict
			OT_input = json.loads(OT_input) 
			LOGS.append(f"Converting OT_input to dict: Success") 
		except Exception as error:
			LOGS.append(f"Converting OT_input to dict: Failled.\nError: {error}") 

	#	SETTINGS
	try : 
		with open("./settings.json") as file :
			settings_file = json.load(file)
		modules_sequence = settings_file["Pipelines"][pipeline_name]#TODO expliciter l'erreur d'une pipeline non connue dans settings.json
		SETTINGS = {
			"pipeline":pipeline_name,
			"modules_sequence": modules_sequence,
			"OT_input": OT_input,
			"modules_settings": {module_name: module_settings #TODO Retirer cette clé intermédiaire ?
				for (module_name, module_settings) in settings_file["modules_settings"].items() 
				if module_name in modules_sequence
			}
		}
		LOGS.append(f"Loading Settings: Success")
	except Exception as error:
		LOGS.append(f"Loading Settings: Failled.\nError: {error}")
		abording_export(LOGS)


	# APPLICATION DES MODULES DE LA PIPELINE
	for module_i in modules_sequence :
		# LOGS.append(f"Calling module {module_i}")
		# try : 
		exec(f"import {module_i}")
		# except Exception as error:
		# 	LOGS.append(f"Failled to import: {module_i}.\nError: {error}")
		# 	abording_export(LOGS, SETTINGS)
		# else:
		# 	try:	
		HANDLINGS, PORT, LOGS, SETTINGS = eval(f"{module_i}.main(HANDLINGS, PORT, LOGS, SETTINGS, module_i)")
			# except Exception as error:
			# 	LOGS.append(f"Failled to run: {module_i}.\nError: {error}")
			# 	abording_export(LOGS, SETTINGS)
	
	#CLOSSING
	LOGS.append(f"End of pipeline {pipeline_name}. Exporting PAS and clossing PAS builder")

	#FIXME uniquement pr tests en local (le PAS est transmit à l'IH par le module idoine)
	if pipeline_name == "GPMB_demo":
		abording_export(LOGS, HANDLINGS, PORT, SETTINGS)


#=========================================================================
def abording_export(LOGS, HANDLINGS= None, PORT= None, SETTINGS= None):
	LOGS.append(f"PAS modelling closing")
	
	export = {
		"LOGS": LOGS,
		"PORT'S ACTIVITIES SCENARIO": HANDLINGS,
		"PORT'S PARAMETERS": PORT,
		"SETTINGS": SETTINGS
		
	}
	
	with open("./PAS_output.json", 'w') as file:
		json.dump(export, file, indent=4, default=str)
	
	print(f"\n\nlogs & settings exported in {file} before closing")
	
	sys.exit(0)# ou bien on considère qu'on est en exit(0) ?



# SHELL
if __name__ == "__main__" :
	parser = argparse.ArgumentParser(description="Process executable options.")

	parser.add_argument(
		"-r", "--OT_input",
		nargs='?', 
		default= None,
		help="Transmited argument from Operational Tools when calling PAS modelling"
	)
	
	parser.add_argument( #TODO en définitive, devrait être un élément contenu dans OT_input, il est gardé de côté (en interne) pr le moment
		"-p", "--pipeline", 
		nargs='?',
		default="energy_consumption_assessment", 
		help="Name of the pipeline to use (see 'settings.json')."
	)

	#TODO : option facultatives à implémenter
	# parser.add_argument(
	#	 "--settingsPath", default="./settings.json", type=str, help="Path to the json file containing settings"
	# )

	# parser.add_argument(
	#	 "-v", "--verbose", default="normal", type=str, help="restricted: only valid records in output.\n normal (default value); balanced output.\n extended: every processing logs insered into output. Use for setting issues identification. May generate trouble for output conversion to graph"
	# )


	args = parser.parse_args()

	main(
		args.pipeline, 
		args.OT_input
	)
