import json
from elasticsearch import Elasticsearch


def main(HANDLINGS, PORT, LOGS, SETTINGS, module_name):
	'''
	#FIXME
	'''
	#INITIALISATION
	LOGS.append(f"==== {module_name}  ====")

	
	# PROCESSING
	for input_component in SETTINGS["OT_input"]["input"]:
		
		#DATA RETRIVING
		
		#IH requesting
		if input_component["category"] == "ih-api": 
			success, answer = IH_requesting(input_component)
			LOGS.append(f"Requesting {input_component['name']} to the IH: {'Success' if success else 'Failled'}") 
			if not success:
				LOGS.append({"cause": answer})
		
		#OT_input parsing
		elif input_component["category"] == "forceInput":
			try:
				answer = [forced_input_component["value"]
					for forced_input_component in SETTINGS["OT_input"]["forceinput"] 
					if forced_input_component['name'] == input_component['name']
				]
				success = True
			except Exception as error:
				success = False
				answer = error
			LOGS.append(f"Parsing {input_component['name']} from the OT input: {'Success' if success else 'Failled'}") 
			if not success:
				LOGS.append({"cause": answer})
		else :
			LOGS.append(f"Unable to recognize {input_component['name']} source: {input_component['category']}")
		
		#DATA AFFECTATION
		if input_component['name'] in ["supplychains", "rules", "resources"]:
			PORT[input_component['name']] = answer
		elif input_component['name'] == "pas-input":
			HANDLINGS = answer
		else :
			LOGS.append(f"Unable to recognize {input_component['name']} destination")


	#CLOTURE
	#LOGS.append(f"====> {module_name} ENDS <====")
	return (HANDLINGS, PORT, LOGS, SETTINGS)


#=========================================================================
def IH_requesting(input_component):
	success = True
	es = Elasticsearch(next(option["value"] for option in input_component["options"] if option["name"] == "url")) #devrait avoir un len de 1
	index = next(option["value"] for option in input_component["options"] if option["name"] == "sourceId")
	#aditional_parameters = next(option.get["value"] for option in input_component["options"] if option["name"] == "reqParams") #Options présente dans CERTAINS PAS_instance.json, mais pas tous
	start_TS = next((option["value"] for option in input_component["options"] if option["name"] == "start"), None)
	end_TS = next((option["value"] for option in input_component["options"] if option["name"] == "end"), None)
	if start_TS == None or end_TS == None:
		subbody = {
			"match_all": {}
		}
	else :
		subbody = {
			"range": {
				"timestamp" : {
					"gte" : start_TS,
					"lte" : end_TS
				}
			}
		}
	
	try:
		raw_answer = es.search(
			index=index, 
			body= {"query": subbody}
		)
		answer = [hit["_source"]["data"] for hit in raw_answer["hits"]["hits"]] #FIXME la sous cl� data ne devrait pas �tre ici, mais � la conversion
	except Exception as error:
		success = False #FIXME on ne catch pas les erreurs de connections comme "ConnectionError('N/A', "(<urllib3.connection.HTTPConnection object at 0x7fb870d39a00>, 'Connection to 192.168.0.13 timed out. (connect timeout=10)')", ConnectTimeoutError(<urllib3.connection.HTTPConnection object at 0x7fb870d39a00>, 'Connection to 192.168.0.13 timed out. (connect timeout=10)'))"
		answer = error

	return success, answer
