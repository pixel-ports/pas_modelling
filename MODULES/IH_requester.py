import json
from elasticsearch import Elasticsearch


def main(HANDLINGS, PORT, LOGS, SETTINGS, module_name):
	"""From Operational Tools, retrives PAS inputs (handling requests -> HANDLINGS and port's parameters -> PORT)
	NB: Here the names and values are inherited from outside PAS model. The modules "handling_converter" and "port_converter" are used to set those elements in proper format 
	"""
	#INITIALISATION
	LOGS.append(f"==== {module_name}  ====")

	
	# PROCESSING
	for input_component in SETTINGS['OT_input']['input']:
		
		#INPUTS RETRIVING
		#	FROM IH
		if input_component['category'] == "ih-api": 
			success, data = request_IH_input(input_component)
			LOGS.append(f"Retriving {input_component['name']} from IH: {'Success' if success else 'Failled'}") 
			if not success:
				LOGS.append({'Details': data})
		
		#	FORCED INPUTS
		elif input_component['category'] == "forceInput": 
			success, data = get_foreced_input(input_component['name'], SETTINGS['OT_input']['forceinput'])
			LOGS.append(f"Retriving {input_component['name']} form forced input: {'Success' if success else 'Failled'}") 
			if not success:
				LOGS.append({'Details': data})
				
		#	OTHER CASE
		else:
			LOGS.append(f"Unable to retrive {input_component['name']} from {input_component['category']}")
		
		#INPUTS PARSING
		if input_component['name'] in ['supplychains', 'rules', 'resources']:#FIXME (lorsque on fera le split de rules)
			PORT[input_component['name']] = data
		elif input_component['name'] == "vesselcalls":
			HANDLINGS = data
		else :
			LOGS.append(f"Unable to reconize {input_component['name']} destination")


	#CLOTURE
	return (HANDLINGS, PORT, LOGS, SETTINGS)


#=========================================================================
def request_IH_input(input_component: dict)-> tuple: #FIXME?
	"""From request's parameters given in OT_input, retrive the input component from IH
	"""
	success = None
	data = None

	try:
		#INITIALIZATION: REQUEST'S PARAMETERS
		es = Elasticsearch(	next(option['value'] for option in input_component['options'] if option['name'] == "url")) #devrait avoir un len de 1
		index = 			next(option['value'] for option in input_component['options'] if option['name'] == "sourceId")
		#aditional_parameters = next(option.get['value'] for option in input_component['options'] if option['name'] == "reqParams") #Options prÃ©sente dans CERTAINS PAS_instance.json, mais pas tous
		start_TS = 			next((option['value'] for option in input_component['options'] if option['name'] == "start"), None) #FIXME uniquement pr handlings ?
		end_TS = 			next((option['value'] for option in input_component['options'] if option['name'] == "end"), None)
		if start_TS == None or end_TS == None:
			subbody = {
				'match_all': {}
			}
		else :
			subbody = {
				'range': {
					'timestamp' : {
						'gte' : start_TS,
						'lte' : end_TS
					}
				}
			}

		#PROCESS: SENT REQUEST
		raw_answer = es.search(
			index=index, 
			body= {'query': subbody}
		)

		#OUTPUT
		success = True
		data = raw_answer['hits']['hits'][0]['_source']['Datas']
				#[hit['_source']['Datas'] for hit in raw_answer['hits']['hits']] #FIXME doit on réellement renvoyer tous les hit, ou uniquement le premier ?

	except Exception as error:
		success = False #FIXME on ne catch pas les erreurs de connections comme "ConnectionError('N/A', "(<urllib3.connection.HTTPConnection object at 0x7fb870d39a00>, 'Connection to 192.168.0.13 timed out. (connect timeout=10)')", ConnectTimeoutError(<urllib3.connection.HTTPConnection object at 0x7fb870d39a00>, 'Connection to 192.168.0.13 timed out. (connect timeout=10)'))"
		data = { 
			'type': "Aborded IH request",
			'item': input_component['name'],				
			'message': f"{error}"
		}

	return success, data


def get_foreced_input(component_name: str, Foreced_components: dict)-> tuple:
	"""From input component name and OT_input forced values list, give the component ['_source'] value
	"""
	success = None
	data = None

	try:
		#INITIALIZATION
		
		#PROCESS
		forced_value = next(forced_input_component['value']['_source']
			for forced_input_component in Foreced_components 
			if forced_input_component['name'] == component_name
		)
		#OUTPUT
		success = True
		data = forced_value

		
	except Exception as error:
		success = False
		data = { 
			'type': "Aborded forced value retriving",
			'item': component_name,				
			'message': f"{error}"
		}

	return success, data