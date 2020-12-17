# -*- coding: utf-8 -*-
import argparse
import json
import sys

sys.path.insert(0, "./MODULES")
import inputs_loader
import outputs_exporter


def main(PAS_instance:dict, local_export:bool, display_logs:bool) :
	'''
	Pour le pipeline passé en argument, appelle successivement les différents modules, leurs passant successivement l'objet "PAS" qui contient l'entièreté des données afférente au scénario.
	'''
	#INITIALIZATION
	LOGS = ["==== PAS modeling started  ===="]  #Array pr fils chronologique FIXME repartir sur le dict, avec text par module, mais aussi un champs "discarted handlings" etc
	log_message = None
	try:
		if PAS_instance == "local":
			path ="./DOCKERISE/PAS_instance_OT.json"
			with open(path) as file :
				PAS_instance = json.load(file)
			log_message = f"from local file {path}"
		else:
			PAS_instance = json.loads(PAS_instance)
		if isinstance(PAS_instance, dict):
			log_status = "success"
			log_message = f"from given argument"
		else:
			log_status = "failed"
			log_message = f"given PAS instance is not a dictionary"
	except Exception as error:
		log_status = "failed"
		log_message = error
	LOGS.append(f"Loading current PAS instance: {log_status} ({log_message})")
	SETTINGS, HANDLINGS, PORT, LOGS = inputs_loader.main(PAS_instance, LOGS)
 
	# MODULES SEQUENCE APPLICATION TO PAS
	for module_i in SETTINGS["pipeline"]:
		# try : 
		exec(f"import {module_i}")
		# except Exception as error:
		# 	LOGS.append(f"Failled to import: {module_i}.Error: {error}")
		# else:
		# 	try:	
		HANDLINGS, PORT, LOGS = eval(f"{module_i}.main(HANDLINGS, PORT, LOGS, SETTINGS[module_i], module_i)")
		# 	except Exception as error:
		# 		LOGS.append(f"Failled to run: {module_i}.Error: {error}")

	#CLOSSING
	LOGS.append(f"==== ENDING  ====")
	LOGS.append(f"End of the run. PAS properly generated, {len(HANDLINGS)} were processed end-to-end. See logs for details") #FIXME faux, on peut ne pas récupérer les info (ex: timeout ES)
	LOGS = outputs_exporter.main(PAS_instance=PAS_instance, LOGS=LOGS, HANDLINGS=HANDLINGS, local_export=local_export)
	if display_logs:
		for item in LOGS:
			print(item)
	sys.exit(0)
#=========================================================================
# SHELL
if __name__ == "__main__" :
	parser = argparse.ArgumentParser(description="Process executable options.")
	#Lecture du fichier local comme valeur par défaut
	
	parser.add_argument(
		"PAS_instance",
		type=str,
		nargs='?', 
		default= "local",
		help="Transmited argument from Operational Tools when calling PAS modelling"
	)
	
	parser.add_argument(
		"--local_export",
		type = bool,
		nargs='?', 
		default= False,
		help="Export outputs as json files in ./OUTPUTS"
	)
	parser.add_argument(
		"--display_logs",
		type = bool,
		nargs='?', 
		default= False,
		help="Display PAS model logs in consol"
	)
	args = parser.parse_args()
	main(
		args.PAS_instance,
		args.local_export,
		args.display_logs
	)
