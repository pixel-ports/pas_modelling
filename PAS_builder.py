# -*- coding: utf-8 -*-
import argparse
import json
import sys

sys.path.insert(0, "./MODULES")
import inputs_loader
import outputs_exporter


def main(PAS_instance:dict) :
	'''
	Pour le pipeline passé en argument, appelle successivement les différents modules, leurs passant successivement l'objet "PAS" qui contient l'entièreté des données afférente au scénario.
	'''
	#INITIALIZATION
	LOGS = ["==== PAS modeling started  ===="]  #Array pr fils chronologique
	log_message = None
	try:
		PAS_instance = json.loads(PAS_instance) 
		log_status = "success" 
	except Exception as error:
		log_status = "failed"
		log_message = error
	LOGS.append(f"Loading current PAS instance: {log_status} (message: {log_message})")	
	HANDLINGS, PORT, LOGS, SETTINGS = inputs_loader.main(PAS_instance, LOGS)
 
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
	LOGS.append(f"End of the run. PAS modeling properly ended, {len(HANDLINGS)} were processed end-to-end. See logs for details")
	outputs_exporter.main(LOGS=LOGS, HANDLINGS=HANDLINGS, export_infos=PAS_instance["output"], abording=False, target='local files') #'IH')#
	print(LOGS)
	sys.exit(0)
#=========================================================================
# SHELL
if __name__ == "__main__" :
	parser = argparse.ArgumentParser(description="Process executable options.")
	#Lecture du fichier local comme valeur par défaut
	with open("./PAS_instance.json" ) as file :
		local_PAS_instance = json.dumps(json.load(file))
	parser.add_argument(
		"-r", "--PAS_instance",
		nargs='?', 
		default= local_PAS_instance,
		help="Transmited argument from Operational Tools when calling PAS modelling"
	)
	args = parser.parse_args()
	main(
		args.PAS_instance
	)
