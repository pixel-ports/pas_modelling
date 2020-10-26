import json
from elasticsearch import Elasticsearch


def main(PAS_instance, LOGS):
	LOGS = ["==== Load inputs ===="]
	raw_inputs = {}
	proper_inputs = {}
	#COLLECT RAW INPUT FROM IH
	for pas_instance_input in PAS_instance.get('input', []):
		raw_inputs.update({pas_instance_input["name"]:send_IH_request(pas_instance_input)})
	#COLLECT RAW INPUT FROM FORCEINPUT
	for pas_instance_input in PAS_instance.get('forceinput', []): #On le place en second car forceinput est prioritaire (doit écraser en cas de doublon)
		raw_inputs.update({pas_instance_input["name"]:pas_instance_input})
	#CONVERT RAW INPUTS TO INPUT 
	proper_inputs = {input_name: extract_data_from_IH_response(input_content) for input_name, input_content in raw_inputs.items()}
	#INPUTS ASSIGNMENTS
	SETTINGS = proper_inputs.pop("settings").get("data")
	HANDLINGS = proper_inputs.pop("vesselCalls").get("data")
	PORT = {}
	for para_name, para_content in proper_inputs.items():
		if para_content['type'][0:3]=="PP>":
			PORT.update({para_name:{key:val for key,val in para_content["data"].items()}})

	
	return HANDLINGS, PORT, LOGS, SETTINGS
#========================================================================= 
def send_IH_request(pas_instance_input:dict)-> dict: #FIXME
	#INITIALIZATION: REQUEST'S PARAMETERS
	es = Elasticsearch(	next(option['value'] for option in pas_instance_input['options'] if option['name'] == "url")) #devrait avoir un len de 1
	index = 			next(option['value'] for option in pas_instance_input['options'] if option['name'] == "sourceId")
	#aditional_parameters = next(option.get['value'] for option in input_component['options'] if option['name'] == "reqParams") #Options prÃ©sente dans CERTAINS PAS_instance.json, mais pas tous
	start_TS = 			next((option['value'] for option in pas_instance_input['options'] if option['name'] == "start"), None) 
	end_TS = 			next((option['value'] for option in pas_instance_input['options'] if option['name'] == "end"), None)
	# Argument supplémentaire pour les vesselCalls
	if start_TS == None or end_TS == None:
		subbody = {
			'match_all': {}
		}
	else:
		subbody = {
			'range': {
				'timestamp' : {
					'gte' : start_TS,
					'lte' : end_TS
				}
			}
		}
	#SENT REQUEST
	answer_hits = es.search(
		index=index, 
		body= {'query': subbody}
	)
	
	return answer_hits

def extract_data_from_IH_response(input_:dict)-> dict:
	hits = input_['value']['hits']['hits']
	if ">collection" in input_["type"]:
		input_["data"] = {key:value for key, value in hits[0]["_source"]["data"].items()}
			#[item["_source"]["data"] for item in hits]	
	elif ">unique_doc" in input_["type"]:
		input_["data"] = input_["data"] = hits[0]["_source"]["data"]#TODO ajouter un catch si plus que 1 items recus
	elif ">list" in input_["type"]:
		input_["data"] = [item["_source"]["data"]for item in hits]
	del input_["value"] #NB on peut aussi passer par .pop en lors de l'assignation à hit
	# else:
	# 	pass #TODO ajouter une levée d'erreur pour cas non reconnu

	return input_
