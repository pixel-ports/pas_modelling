import json
from elasticsearch import Elasticsearch


def main(PAS_instance, LOGS):
	LOGS = ["==== Load inputs ===="]
	#COLLECT INPUTS
	inputs = {}
	for ih_input in PAS_instance.get('input', []):
		inputs.update({ih_input["name"]:get_IH_input(ih_input)})
	for forced_input in PAS_instance.get('forceinput', []): #On le place en second car forceinput est prioritaire (doit écraser en cas de doublon)
		inputs.update({forced_input["name"]:forced_input})
	#DISPATCH INPUTS
	SETTINGS = inputs.pop("settings").get("value")
	HANDLINGS = inputs.pop("vesselCalls").get("value")
	PORT = {} #TODO ne pas s'appuyer sur prendre tous après les pop, mais bien filtrer sur PP
	for para_name, para_content in inputs.items():
		if para_content["type"] == "PortParameter":
			PORT.update({para_name:{key:val for key,val in para_content["value"].items()}})
	#ENDING
	return SETTINGS, HANDLINGS, PORT, LOGS 
#========================================================================= 
def get_IH_input(ih_input:dict)-> dict:
	#INITIALIZATION: REQUEST'S PARAMETERS
	es_arg = {option["name"]:option["value"] for option in ih_input["options"]}
	start_TS = es_arg.get("start", None)
	end_TS = es_arg.get("end", None)
	query = {'query': {'match_all': {}}}
	if None not in [start_TS, end_TS]:
		query = {'query': {'range': {'data.scheduled_arrival_dock': {'gte' : start_TS,'lte' : end_TS}}}}
	#SENT REQUEST #FIXME ajouter gestion des timeout
	answer_hits = Elasticsearch(es_arg["url"]).search(
		index= es_arg["index"], 
		body= query
	)#["hits"]["hits"]
	#EXTRACT DATA
	if ih_input["format"] == "collection":
		ih_input["value"] = {key:value for document in answer_hits for key, value in document["_source"]["data"].items()}
	elif ih_input["format"] == "tree":
		ih_input["value"] = answer_hits[0]["_source"]["data"]#TODO ajouter un catch si plus que 1 items recus
	elif ih_input["format"] == "list":
		ih_input["value"] = [item["_source"]["data"]for item in answer_hits]
	return ih_input["value"]
