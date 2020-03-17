import argparse
import os
import logging
import json

os.system("clear") 
logging.basicConfig(
	level= logging.INFO, 
	format='%(name) -8s %(message)s')
logger = logging.getLogger("MAIN")


def main(pipeline_name, request_IH) :
	'''
	Pour le pipeline passé en argument, appelle successivement les différents modules, leurs passant successivement l'objet "PAS" qui contient l'entièreté des données afférente au scénario.
	'''
	
	# INITIALISATION
	LOGS = [] #Array pr fils chronologique
	PORT = {} #Ancien nom : PARAMETERS
	HANDLINGS = request_IH
	try : #Chargement SETTINGS
		with open("./settings.json") as file :
			SETTINGS = json.load(file)
		pipeline_modules = SETTINGS["pipelines"][pipeline_name]
		LOGS.extend([
			f"pipeline: {pipeline_name}",
			f"Settings loaded successfully",
			f"modules: {pipeline_modules}",
			]
		)
	except :
		LOGS.append(f"Unable to load {file}, PAS modelling aborded")


	# APPLICATION DES MODULES DE LA PIPELINE
	for module_i in pipeline_modules :
		LOGS.append(f"Calling module {module_i}")
		
		try : 
			exec('from modules.' + module_i + " import " + module_i )#, locals(), globals())
			LOGS.extend([
				f"Module {module_i} imported successfully",
				{module_i + "_settings": SETTINGS['modules_settings'][module_i]}
				]
			) 			
			HANDLINGS, PORT, logs_module = eval(module_i + "(HANDLINGS, PORT, SETTINGS['modules_settings'][module_i])")
			LOGS.extend([
				{module_i + "_internal_logs": logs_module},
				f"Module {module_i} executed successfully" #TODO: ajouter au renvois des modules un status, indiquant le succes ou pas
			]
		)

		except :
			LOGS.append(f"Issue on calling module {module_i}")


	# CLOTURE
	## Export du PAS
	try:
		## Définition du PAS
		PAS = {
			"Handlings": HANDLINGS,
			"Port":PORT,
			"Logs": LOGS
		}
		#FIXME: module d'export à faire
		LOGS.append(f"PAS exported, PAS modelling closing")
	except:
		LOGS.append(f"Unable to export PAS, PAS modelling closing")



#=========================================================================
# SHELL
if __name__ == "__main__" :
	parser = argparse.ArgumentParser(description="Process executable options.")

	parser.add_argument(
		"-r", "--request_IH",
		nargs='?', 
		default= {
			"input": [
				{
					"name": "Handlings",
					"endpoint": "./inputs/GPMB/IH_2018.json",
					"type": "Vessel_Calls",
				},
				{
					"name": "Asignations",
					"endpoint": "./inputs/GPMB/Assignations.json",
					"type": "Port_parameters",
				},
				{
					"name": "Supplychains",
					"endpoint": "./inputs/GPMB/Supplychains.json",
					"type": "Port_parameters",
				},
				{
					"name": "Resources",
					"endpoint": "./inputs/GPMB/Resources.json",
					"type": "Port_parameters",
				}
			]
		},
		help="IH's calling request to obtaining data."
	)
	
	parser.add_argument(
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

	# parser.add_argument(
	#	 "-m", "--monitor", default=False, action="store_true", help="Start monitoring server"
	# )

	args = parser.parse_args()

	main(
		args.pipeline, 
		args.request_IH
	)
