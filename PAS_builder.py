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
	try:
		PAS_instance = json.loads(PAS_instance) 
		log_status = "success" 
	except Exception as error:
		log_status = "failed"
		log_message = error
	LOGS.append(f"Loading current PAS instance: {log_status} (message: {log_message})")	
	
	# INPUTS LOADING
	inputs = {} 
	for input_ in PAS_instance['input']:
		log_item = input_["name"]
		log_source = "remote (IH)"
		success, data = get_IH_data(input_)#FIXME faire la fonction
		if success:
			input_["data"]= data
			inputs.update({input_["name"]:input_})
		LOGS.append(f"Load input {log_item} data from {log_source}: {success}")
		if not success:
			LOGS.append({"error": data})
	for input_ in PAS_instance['forceinput']: #On le place en second car forceinput est prioritaire (doit écraser en cas de doublon)
		log_item = input_["name"]
		log_source = "forced input in PAS_instance"
		try:
			if ">collection" in input_["type"]:
				input_["data"] = [item["_source"]["data"] for item in input_['value']['hits']['hits']]	
			elif ">tree" in input_["type"]:
				input_["data"] = input_['value']['hits']['hits'][0]["_source"]["data"]
			elif ">list" in input_["type"]:
				input_["data"] = input_['value']['hits']['hits'][0]["_source"]["data"]
			else:
				pass #TODO ajouter une levée d'erreur pour cas non reconnu
			success = True
			inputs.update({input_["name"]:input_})
		except Exception as error:
			success = False
			data = error 
		LOGS.append(f"Load input {log_item} data from {log_source}: {success}")
		if not success:
			LOGS.append({"error": data})
	#DISPATCH INPUTS
	SETTINGS = inputs["settings"]["data"] #{name:content for name, content in inputs.items() if content['type'][0:3]=="set"}
	HANDLINGS = inputs["vesselCalls"]["data"] #[content["data"] for name, content in inputs.items() if content['name']=='vesselCalls']
	PORT = {}
	for para_name, para_content in inputs.items():
		if para_content['type'][0:3]=="PP>":
			PORT.update({para_name:{}})
			for item in para_content["data"]:
				PORT[para_name].update(item)
 
# APPLICATION DES MODULES DE LA PIPELINE
	for module_i in SETTINGS["pipeline"] :
		#UNPROTECTED RUN NB for dev & debug
		exec(f"import {module_i}")
		HANDLINGS, PORT, LOGS = eval(f"{module_i}.main(HANDLINGS, PORT, LOGS, SETTINGS[module_i], module_i)")
		#PROTECTED RUN	 NB for prod #FIXME
		# try : 
		# 	exec(f"import {module_i}")
		# except Exception as error:
		# 	LOGS.append(f"Failled to import: {module_i}.Error: {error}")
		# 	export_local_output_file(logs=LOGS, PAS=HANDLINGS, PAS_instance=PAS_instance)
		# else:
		# 	try:	
		# 		HANDLINGS, PORT, LOGS, SETTINGS = eval(f"{module_i}.main(HANDLINGS, PORT, LOGS, SETTINGS, module_i)")
		# 	except Exception as error:
		# 		LOGS.append(f"Failled to run: {module_i}.Error: {error}")
		# 		export_local_output_file(logs=LOGS, PAS=HANDLINGS, PAS_instance=PAS_instance)
	
#CLOSSING
	LOGS.append(f"==== main  ====")
	LOGS.append(f"End of the run. PAS modeling properly ended, {len(HANDLINGS)} were processed end-to-end. See logs for details")
	export_local_output_file(logs=LOGS, PAS=HANDLINGS, PAS_instance=PAS_instance, abording= False) #FIXME debug
	print(LOGS)
	sys.exit(0)
#=========================================================================
def get_IH_data(input_:dict)-> (bool, dict): #FIXME
	success = False
	data = None
	try:
		# if "collection" in input_["type"]: #on doit rendre une liste de n items
		# 	data = [document["_source"]["data"] for document in reponse_ES['value']['hits']['hits']]	
		# elif "tree" in input_["type"]:
		# 	data = reponse_ES['value']['hits']['hits'][0]["_source"]["data"]
		success = True	
	except Exception as error:
		success = False
		data = error
	return success, data

def export_local_output_file(logs, PAS=None, PAS_instance=None, abording=True):
	if abording:
		logs.append(f"Crashed, last log: {logs[-1]} ")
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
