# -*- coding: utf-8 -*-

import argparse
# import os
# import logging
import json

# os.system("clear") 
# logging.basicConfig(
# 	level= logging.INFO, 
# 	format='%(name) -8s %(message)s')
# logger = logging.getLogger("MAIN")


def main(pipeline_name, OT_input) :
	'''
	Pour le pipeline passé en argument, appelle successivement les différents modules, leurs passant successivement l'objet "PAS" qui contient l'entièreté des données afférente au scénario.
	'''
	# INITIALISATION
	HANDLINGS = [] #Liste des vessel calls à traiter
	PORT = {} #Conteneur pour l'ensemble des paramètres décrivant le port
	LOGS = [f"Starting PAS modelling: {pipeline_name}"] #Array pr fils chronologique
		#SETTINGS
	try : 
		with open("./settings.json") as file :
			settings_file = json.load(file)
			modules_sequence = settings_file["pipelines"][pipeline_name]
			SETTINGS = {
				"pipeline":pipeline_name,
				"modules_sequence": modules_sequence,
				"OT_input": OT_input,
				"modules_settings": {module_name: module_settings 
					for (module_name, module_settings) in settings_file["modules_settings"].items() 
					if module_name in modules_sequence
				}
			}
			LOGS.append(f"Settings loaded successfully")
	except :
		LOGS.append(f"Unable to load {file}, PAS modelling aborded")
		#FIXME Exporter logs !


	# APPLICATION DES MODULES DE LA PIPELINE
	for module_i in modules_sequence :
		LOGS.append(f"Calling module {module_i}")
		# try : #Le try est désactivé pr faciliter le debuggage
		exec('from modules.' + module_i + " import " + module_i )#, locals(), globals())
		LOGS.append(f"Module {module_i} imported successfully")
			
		HANDLINGS, PORT, LOGS, SETTINGS = eval(module_i + "(HANDLINGS, PORT, LOGS, SETTINGS, module_i)") #On peut envisager de recevoir aussi SETTINGS pour qu'un module puisse modifier le comportement d'un suivant. A voir

	#CLOSSING
	LOGS.append(f"End of pipeline {pipeline_name}. Clossing PAS builder")

	export = {
		"SETTINGS": SETTINGS,
		"LOGS": LOGS
	}
	with open("./export_run_report.json", 'w') as file:
		json.dump(export, file, indent=4, default=str)
#=========================================================================
# SHELL
if __name__ == "__main__" :
	parser = argparse.ArgumentParser(description="Process executable options.")

	parser.add_argument(
		"-r", "--OT_input",
		nargs='?', 
		default= "",
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
