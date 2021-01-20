import json
from elasticsearch import Elasticsearch


def main(PAS_instance, LOGS):
	LOGS.append("==== Load inputs ====")
	#COLLECT INPUTS
	#Simplified inputs
	inputs = {
		# "settings":{},
		# "vessel_calls":{},
		# "port_parameters":{},
	}
	index_prefix = "pas_test_default_"
	for ih_target in PAS_instance.get('input', []):
		if ih_target["type"] not in inputs:
			inputs[ih_target["type"]] = {}
		success, data = get_IH_input(ih_target, index_prefix)
		if success:
			inputs[ih_target["type"]][ih_target["name"]] = data
			LOGS.append(f'Success to retrieve {ih_target["name"]} (message:{data})')
		else:
			LOGS.append(f'Failed to retrieve {ih_target["name"]} (message:{data})')
	
	for forced_input in PAS_instance.get('forceinput', []): #On le place en second car forceinput est prioritaire (doit écraser en cas de doublon)
		if forced_input["type"] not in inputs:
			inputs[forced_input["type"]] = {}
		inputs[forced_input["type"]][forced_input["name"]] = forced_input["value"]
		LOGS.append(f'Loaded {forced_input["name"]} (from force-inputs')

	if inputs.get("pas_setting", {}) == {}:
		with open("./default_settings.json") as file :
			inputs.update({"pas_setting":json.load(file)})
		LOGS.append(f'Failed to retrieve pas_setting (use default ./default_settings.json)')
	#DISPATCH INPUTS
	SETTINGS = inputs.get("pas_setting", {})
	HANDLINGS = inputs.get("vessel_call", [])
	PORT = inputs.get("port_parameter", {})
	#ENDING
	return SETTINGS, HANDLINGS, PORT, LOGS 
#========================================================================= 
def get_IH_input(ih_target:dict, index_prefix: str)-> dict:
	#INITIALIZATION: REQUEST'S PARAMETERS
	data = None
	success = None
	options = {option["name"]:option["value"] for option in ih_target["options"]}
	url = None
	index = options.get("index_id", '')
	if index == '':
		index = (index_prefix+ih_target["type"])
		if ih_target["type"] == "vessel_call":
			index = "arh-lts-vesselcall" #FIXME magic string pr l'index par défaut des vessel_calls pour GPMB
	# if default_IH_settings.get("elastic_serveur_url", '') != '': #'' is default value
	# 	url = default_IH_settings["elastic_serveur_url"]

	# if options.get("index_id", '') == '': #'' is default value
	# 	options["index_id"] = default_IH_settings["default_input_index_prefix"] + ih_target["name"]

	doc_id = options.get("document_id", '')
	if doc_id == '':
		doc_id = None
	query = {'query': {'match_all': {}}}
	
	start_TS = options.get("start", None)
	end_TS = options.get("end", None)
	if None not in [start_TS, end_TS]:
		query = {'query': {'range': {'data.scheduled_arrival_dock': {'gte' : start_TS,'lte' : end_TS}}}} #FIXME Ne fonctionne plus (même avec un index avec le champs en date sur elastic)
	
	#SENT REQUEST #TODO mettre au propre les erreurs (notamment timeout, index ou doc abscent)
	not_IH_settings = ih_target["name"]!= "ih_settings"
	not_empty_index = index != ''
	if not_IH_settings & not_empty_index:
		#es = Elasticsearch(url)
		try:
			answer_hits = Elasticsearch(url).search(
				index= index.lower(), 
				body= query,
				id= doc_id
				#TODO lorsque l'OT aura implémenté le passage des arguments de doc_ID, implémenter filtres inclusif et exclusif des doc_ids
			)["hits"]["hits"]
			#EXTRACT DATA
			# if ih_target["name"] in ["contenttypes", "supplychains", "resources", "energies", "timetables"]:
			# 	data = {document["_source"]["info"]["ID"]:document["_source"]["data"] for document in answer_hits}

			# elif ih_target["name"] in ["pas_settings", "priority"]:
			# 	data = answer_hits[0]["_source"]["data"]#TODO ajouter un catch si plus que 1 items recus

			if ih_target["type"] == "vessel_call":
				data = [item["_source"]["data"] for item in answer_hits]
			else:
				data = answer_hits[0]["_source"] #{document["_source"]["info"]["ID"]:document["_source"]["data"] for document in answer_hits} #TODO on devrait avoir gardé la distinction info et data des doc, comme sur le DM des vessel calls, mais comme ProDev ne le fournit pas, on fait pas
			success = True
		except Exception as error:
			success = False
			data = error
	return success, data
