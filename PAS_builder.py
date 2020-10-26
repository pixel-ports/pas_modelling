# -*- coding: utf-8 -*-
import argparse
import json
import sys

sys.path.insert(0, "./MODULES")
import inputs_loader


def main(PAS_instance:dict) :
	'''
	Pour le pipeline passé en argument, appelle successivement les différents modules, leurs passant successivement l'objet "PAS" qui contient l'entièreté des données afférente au scénario.
	'''
	#INITIALIZATION
	LOGS = ["==== PAS modeling started  ===="]  #Array pr fils chronologique
		# PAS_instance loading
	log_message = None
	try:
		PAS_instance = json.loads(PAS_instance) 
		log_status = "success" 
	except Exception as error:
		log_status = "failed"
		log_message = error
	LOGS.append(f"Loading current PAS instance: {log_status} (message: {log_message})")	
		# inputs loading
	HANDLINGS, PORT, LOGS, SETTINGS = inputs_loader.main(PAS_instance, LOGS)
 
	# MODULES SEQUENCE APPLICATION TO PAS
	for module_i in SETTINGS["pipeline"] :
		# try : 
		exec(f"import {module_i}")
	# except Exception as error:
	# 	LOGS.append(f"Failled to import: {module_i}.Error: {error}")
	# 	export_local_output_file(logs=LOGS, PAS=HANDLINGS, PAS_instance=PAS_instance)
	# else:
# 	try:	
		HANDLINGS, PORT, LOGS = eval(f"{module_i}.main(HANDLINGS, PORT, LOGS, SETTINGS[module_i], module_i)")
# 	except Exception as error:
# 		LOGS.append(f"Failled to run: {module_i}.Error: {error}")
# 		export_local_output_file(logs=LOGS, PAS=HANDLINGS, PAS_instance=PAS_instance)
	
	#CLOSSING
	LOGS.append(f"==== ENDING  ====")
	LOGS.append(f"End of the run. PAS modeling properly ended, {len(HANDLINGS)} were processed end-to-end. See logs for details")
	export_local_output_file(logs=LOGS, PAS=HANDLINGS, PAS_instance=PAS_instance, abording= False) #FIXME debug
	print(LOGS)
	sys.exit(0)
#=========================================================================


def export_local_output_file(logs, PAS=None, PAS_instance=None, abording=True):
	if abording:
		message = f"Crashed, last log: {logs[-1]}"
		logs.append(message)
		print(message)
	logs.append(f"PAS outputs export to local files before closing")
	folder = "./OUTPUTS/"
	exports = {
		"PAS": PAS,
		"internalLog": logs,
		"PAS_instance" : PAS_instance
	}
	for title, content in exports.items():
		file_path = folder + title + ".json"
		with open(file_path, 'w') as file:
			json.dump(content, file, indent=4, default=str)
		print(f"{title} exported in {file.name}")
	print(f"\nClosing. Bye")
	if abording:
		sys.exit(1)

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
