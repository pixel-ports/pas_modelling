# -*- coding: utf-8 -*-

import argparse
import json
import sys
sys.path.insert(0, "./MODULES")


def main(PAS_instance) :
	'''
	Pour le pipeline passé en argument, appelle successivement les différents modules, leurs passant successivement l'objet "PAS" qui contient l'entièreté des données afférente au scénario.
	'''
# INITIALISATION
	LOGS = ["==== PAS modeling started  ===="]  #Array pr fils chronologique
	# PAS_INSTANCE LOADING
	log_message = None
	if PAS_instance == "local_PAS_instance":
		file_path = "./PAS_instance.json" 
		log_source = f"local file {file_path}"
		try:
			with open(file_path) as file :
				PAS_instance = json.load(file)
				log_status = "success"
		except Exception as error:
			log_status = "failed"
			log_message = error
	else :
		log_source = f"Operational Tools"
		try:
			PAS_instance = json.loads(PAS_instance) 
			log_status = "success" 
		except Exception as error:
			log_status = "failed"
			log_message = error
	LOGS.append(f"Loading current PAS instance data from {log_source}: {log_status} (message: {log_message})")	
	
	# INPUTS LOADING
	inputs = {} 
	for input_ in PAS_instance['input']: #TODO ajouter gestion log
		log_item = input_["name"]
		if input_["category"] == "forceInput":
			log_source = f"forced input in PAS_instance"
			for forced_input in PAS_instance['forceinput']:
				if input_["name"] == forced_input["name"]:
					if "collection" in input_["type"]:
						input_["data"] = [item["_source"]["data"] for item in forced_input['value']['hits']['hits']]	
					elif "tree" in input_["type"]:
						input_["data"] = forced_input['value']['hits']['hits'][0]["_source"]["data"]
					else:
						pass #TODO ajouter une levée d'erreur pour cas non reconnu
					log_status = "success"
		elif input_["category"] == "ih-api":
			log_source = f"remote (IH)"	
			input_["data"] = get_IH_data(input_)
		inputs.update(input_)
		LOGS.append(f"Loading input {log_item} data from {log_source}: {log_status} (message: {log_message})")
		
	


		SETTINGS = {input_["name"]:input_ for input_ in PAS_instance['input'] if input_["type"]=="settings"}
		:
			if input_["name"]=="settings":
				if input_["category"] == "forceInput": #FIXME faire le cas "pas en force input"
					source = f"forced input in PAS_instance"
					for input_ in PAS_instance['forceinput']:
						if input_["name"]=="settings":
							SETTINGS = input_['value']['hits']['hits'][0]['_source']['data']
							status = "success"	
				else: 
					source = f"Information Hub"
					status = "failed"	
					pass #FIXME faire le cas "pas en force input", cad que la valeur de SETTINGS est soit à aller chercher ds l'IH, soit à charger à partir d'un fichier de settings par défaut. Probablement en éclatant le module de call à l'IH en une fonction qui peut être appeller ici (et à chaque fois qu'un en a besoin).	
	except Exception as error:
			status = "failed"
			message = error
	LOGS.append(f"Loading settings data from {source}: {status} (message: {message})")
	#OTHER COMPONENTS
	<<idem
	HANDLINGS = [] #Liste des vessel calls à traiter
	PORT = {} #Conteneur pour l'ensemble des paramètres décrivant le port

	# APPLICATION DES MODULES DE LA PIPELINE
	modules_sequence = SETTINGS.keys()
	for module_i in modules_sequence :
		
		#UNPROTECTED RUN
		exec(f"import {module_i}")
		HANDLINGS, PORT, LOGS, SETTINGS = eval(f"{module_i}.main(HANDLINGS, PORT, LOGS, SETTINGS, module_i)")
		
		#PROTECTED RUN	
		# try : 
		# 	exec(f"import {module_i}")
		# except Exception as error:
		# 	LOGS.append(f"Failled to import: {module_i}.Error: {error}")
		# 	export_local_output_file(LOGS, SETTINGS)
		# else:
		# 	try:	
		# 		HANDLINGS, PORT, LOGS, SETTINGS = eval(f"{module_i}.main(HANDLINGS, PORT, LOGS, SETTINGS, module_i)")
		# 	except Exception as error:
		# 		LOGS.append(f"Failled to run: {module_i}.Error: {error}")
		# 		export_local_output_file(LOGS, SETTINGS)
	
	#CLOSSING
	LOGS.append(f"==== main  ====")
	LOGS.append(f"End of pipeline {pipeline_name}.")

	print(f"PAS_builder ended, {len(HANDLINGS)} were processed end-to-end. See logs for details")
	if "local" in pipeline_name:
		export_local_output_file(LOGS, HANDLINGS, PORT, SETTINGS, abording= False)
	print(f"=============================================================================")	
	print(f"PAS builder internal logs: {json.dumps(LOGS, indent=4, default=str)}")
	
	sys.exit(0)
#=========================================================================
def get_IH_data(input_:dict)-> dict:
	pass #FIXME 
'''
	if "collection" in input_["type"]: #on doit rendre une liste de n items
		data = [document["_source"]["data"] for document in reponse_ES['value']['hits']['hits']]	
	elif "tree" in input_["type"]:
		data = reponse_ES['value']['hits']['hits'][0]["_source"]["data"]		
	return data	
'''

def export_local_output_file(LOGS, HANDLINGS= None, PORT= None, SETTINGS= None, abording= True):
	LOGS.append(f"PAS modelling closing")
	
	export = {
		"LOGS": LOGS,
		"ACTIVITIES": HANDLINGS,
		"PORT'S PARAMETERS": PORT,
		"SETTINGS": SETTINGS	
	}
	
	with open("./PAS_output.json", 'w') as file:
		json.dump(export, file, indent=4, default=str)
	
	print(f"\n\nLocal PAS builder run detected. PAS, logs & settings exported in {file.name} before closing") 


	if abording:
		sys.exit(1)

# SHELL
if __name__ == "__main__" :
	parser = argparse.ArgumentParser(description="Process executable options.")

	parser.add_argument(
		"-r", "--PAS_instance",
		nargs='?', 
		default= None,
		help="Transmited argument from Operational Tools when calling PAS modelling"
	)
	
	parser.add_argument( #TODO en définitive, devrait être un élément contenu dans PAS_instance, il est gardé de côté (en interne) pr le moment
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
		args.PAS_instance
	)
