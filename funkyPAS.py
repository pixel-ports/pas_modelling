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
	PAS = {
		"state": request_IH,
		"parameters": {},
		"logs": {
			"run": []
		}
	}

	try :
		with open("./settings.json") as file :
			settings = json.load(file)
		pipeline = settings["pipelines"][pipeline]
		message = f"Loaded settings" ; PAS["logs"]["run"].append(message) ; logger.warning(message)
	except :
		message = f"Unable to load {file}, PAS modelling aborded" ; PAS["logs"]["run"].append(message) ; logger.warning(message) #Techniquement, inutile sauf si on ajoute un export du PAS ici


	# APPELE DES MODULES DE LA PIPELINE
	# for module_i in pipeline :
	# 	message = f"Calling module {module_i}" ; PAS["logs"]["run"].append(message) ; logger.warning(message)
		
	# 	try : 
	# 		exec('from modules.' + module_i + " import " + module_i )#, locals(), globals())
	# 		PAS = eval(module_i + "(PAS, settings['modules_settings'].get(module_i, [], str(module_i))")
	# 		message = (f"Module {module_i} executed successfully") ; PAS["logs"]["run"].append(message) ; logger.warning(message)

	# 	except :
	# 		message = (f"Issue on calling module {module_i}") ; PAS["logs"]["run"].append(message) ; logger.warning(message)
	# 		break
	# CLOTURE
	try:
		#EXPORT DU PAS
		message = (f"PAS export, PAS modelling closing") ; PAS["logs"]["run"].append(message) ; logger.warning(message)
		#TODO: export du PAS
	except:
		message = (f"Unable to export PAS, PAS modelling closing") ; PAS["logs"]["run"].append(message) ; logger.warning(message)

#=========================================================================
def log(message, logs_leaf = PAS["logs"]["run"], source_name = module_i):
	logs_leaf.append(message)
	logging.getLogger(source_name).warning(message)

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
