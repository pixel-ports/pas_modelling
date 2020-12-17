import json
from elasticsearch import Elasticsearch


def main(PAS_instance, LOGS):
	LOGS.append("==== Load inputs ====")
	#COLLECT INPUTS

	default_IH_settings = {option["name"]:option["value"] for item in PAS_instance['input'] for option in item["options"] if item["name"]=="ih_settings"}

	inputs = {}
	for ih_target in PAS_instance.get('input', []):
		if ih_target["name"] != "ih_settings":
			success, data = get_IH_input(ih_target, default_IH_settings)
			if success:
				inputs.update({ih_target["name"]:data})
			else:
				LOGS.append(f'Failed to retrieve {ih_target["name"]} (message:{data}')
	for forced_input in PAS_instance.get('forceinput', []): #On le place en second car forceinput est prioritaire (doit écraser en cas de doublon)
		inputs.update({forced_input["name"]:forced_input})
	#DISPATCH INPUTS
	SETTINGS = inputs.pop("pas_settings")#FIXME remplacer par un get (et donc filtrer pour PORT)
	SETTINGS.update(default_IH_settings)
	HANDLINGS = inputs.pop("vesselcalls")
	PORT = inputs
	#ENDING
	return SETTINGS, HANDLINGS, PORT, LOGS 
#========================================================================= 
def get_IH_input(ih_target:dict, default_IH_settings:dict)-> dict:
	#INITIALIZATION: REQUEST'S PARAMETERS
	data = None
	success = None
	options = {option["name"]:option["value"] for option in ih_target["options"]}
	url = None
	if default_IH_settings.get("elastic_serveur_url", '') != '': #'' is default value
		url = default_IH_settings["elastic_serveur_url"]

	if options.get("index_id", '') == '': #'' is default value
		options["index_id"] = default_IH_settings["default_input_index_prefix"] + ih_target["name"]

	start_TS = options.get("start", None)
	end_TS = options.get("end", None)
	query = {'query': {'match_all': {}}}
	# if 0 not in [start_TS, end_TS]:
	# 	query = {'query': {'range': {'data.scheduled_arrival_dock': {'gte' : start_TS,'lte' : end_TS}}}} #FIXME Ne fonctionne plus (même avec un index avec le champs en date sur elastic)
	
	#SENT REQUEST #TODO mettre au propre les erreurs (notamment timeout, index ou doc abscent)
	not_IH_settings = ih_target["name"]!= "ih_settings"
	not_empty_index = options["index_id"] != ''
	if not_IH_settings & not_empty_index:
		#es = Elasticsearch(url)
		try:
			answer_hits = Elasticsearch(url).search(
				index= options["index_id"].lower(), 
				body= query
				#TODO lorsque l'OT aura implémenté le passage des arguments de doc_ID, implémenter filtres inclusif et exclusif des doc_ids
			)["hits"]["hits"]
			#EXTRACT DATA
			if ih_target["name"] in ["contenttypes", "supplychains", "resources", "energies", "timetables"]:
				data = {document["_source"]["info"]["ID"]:document["_source"]["data"] for document in answer_hits}

			elif ih_target["name"] in ["pas_settings", "priority"]:
				data = answer_hits[0]["_source"]["data"]#TODO ajouter un catch si plus que 1 items recus
			elif ih_target["name"] == "vesselcalls":
				data = [item["_source"]["data"]for item in answer_hits]
			success = True
		except Exception as error:
			success = False
			data = error
	return success, data
