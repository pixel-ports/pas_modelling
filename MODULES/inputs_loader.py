import json
from elasticsearch import Elasticsearch


def main(PAS_instance, LOGS):
	LOGS = ["==== Load inputs ===="]
	#COLLECT INPUTS
	# for input_item in PAS_instance.get('input', {}):
		# print({input_item["name"]: input_content})
	# 	if input_name=="IH_settings":

	# {ih_input["name"]:get_IH_input(ih_input) for ih_input in PAS_instance.get('input', []) if ih_input["name"]=="IH_settings"}
	
	# PAS_instance['input'][0]['name']
	inputs = {}
	for ih_target in PAS_instance.get('input', []):
		inputs.update({ih_target["name"]:get_IH_input(ih_target)})
	for forced_input in PAS_instance.get('forceinput', []): #On le place en second car forceinput est prioritaire (doit écraser en cas de doublon)
		inputs.update({forced_input["name"]:forced_input})
	#DISPATCH INPUTS
	#inputs.pop("IH_settings")
	SETTINGS = inputs.pop("PAS_settings")
	HANDLINGS = inputs.pop("vesselCalls")
	PORT = inputs
	#ENDING
	return SETTINGS, HANDLINGS, PORT, LOGS 
#========================================================================= 
def get_IH_input(ih_target:dict)-> dict:
	#INITIALIZATION: REQUEST'S PARAMETERS
	ih_target["value"] = None
	options = {option["name"]:option["value"] for option in ih_target["options"]}

	# index_prefix = "pas_test_input_"#FIXME
	# if options.get("index_id", '') == '':
	# 	index = index_prefix + ih_input["name"].lower()

	start_TS = options.get("start", None)
	end_TS = options.get("end", None)
	query = {'query': {'match_all': {}}}
	if None not in [start_TS, end_TS]:
		query = {'query': {'range': {'data.scheduled_arrival_dock': {'gte' : start_TS,'lte' : end_TS}}}}
	
	#SENT REQUEST #FIXME ajouter gestion des timeout et autres sources erreurs
	if options.get("index_id", '') != '': 
		answer_hits = Elasticsearch(options.get("url", None)).search(
			index= options["index_id"], 
			body= query
		)["hits"]["hits"]

		#EXTRACT DATA
		if ih_target["name"] in ["contentTypes", "supplychains", "resources", "energies", "timetables"]:
			ih_target["value"] = {document["_source"]["info"]["ID"]:document["_source"]["data"] for document in answer_hits}

		elif ih_target["name"] in ["PAS_settings", "priority_tree"]:
			ih_target["value"] = answer_hits[0]["_source"]["data"]#TODO ajouter un catch si plus que 1 items recus
		elif ih_target["name"] == "vesselCalls":
			ih_target["value"] = [item["_source"]["data"]for item in answer_hits]
	return ih_target["value"]
