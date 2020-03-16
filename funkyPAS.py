import argparse
import os
import logging
import json

os.system("clear") 
logging.basicConfig(
	level= logging.INFO, 
	format='%(name) -8s %(message)s')
logger = logging.getLogger("MAIN")


def main(pipeline, request_IH) :
	'''
	Pour le pipeline passé en argument, appelle successivement les différents modules, leurs passant successivement l'objet "PAS" qui contient l'entièreté des données afférente au scénario.
	'''
		
	# INITIALISATION
	HANDLINGS = {request_IH} 
	PARAMETERS = {}  
	LOGS = []
	SETTINGS = {} 

	try :
		with open("./settings.json") as file :
			SETTINGS = json.load(file)
		pipeline = SETTINGS["pipelines"][pipeline]
		LOGS.append(f"Settings loaded successfully")
	except :
		message = f"Unable to load {file}, PAS modelling aborded" ; LOGS.append(message) ; logger.warning(message) #Techniquement, inutile sauf si on ajoute un export du PAS ici


	# APPELE DES MODULES DE LA PIPELINE
	for module_i in pipeline :
		message = f"Calling module {module_i}" ; LOGS.append(message) ; logger.warning(message)
		LOGS.append({module_i:[]})
		exec('from modules.' + module_i + " import " + module_i )#, locals(), globals())
		eval(module_i + "(HANDLINGS, PARAMETERS, LOGS[-1][module_i], SETTINGS['modules_settings'][module_i])")
		message = (f"Module {module_i} executed successfully") ; LOGS.append(message) ; logger.warning(message)
		# try : 
		# 	exec('from modules.' + module_i + " import " + module_i )#, locals(), globals())
		# 	PAS = eval(module_i + "(PAS, settings['modules_settings'].get(module_i, [], str(module_i))")
		# 	message = (f"Module {module_i} executed successfully") ; PAS["logs"]["run"].append(message) ; logger.warning(message)

		# except :
		# 	message = (f"Issue on calling module {module_i}") ; PAS["logs"]["run"].append(message) ; logger.warning(message)
		# 	break


	# CLOTURE
	try:
		#EXPORT DU PAS
		message = (f"PAS exported, PAS modelling closing") ; LOGS.append(message) ; logger.warning(message)
		#TODO: export du PAS
	except:
		message = (f"Unable to export PAS, PAS modelling closing") ; LOGS.append(message) ; logger.warning(message)

#=========================================================================
# SHELL
if __name__ == "__main__" :
	parser = argparse.ArgumentParser(description="Process executable options.")

	parser.add_argument(
		"-r", "--request_IH",
		nargs='?', 
		default= None, 
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
