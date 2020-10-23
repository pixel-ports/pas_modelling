# import json
# from typing import Iterable
# import jsonschema
from elasticsearch import Elasticsearch
from elasticsearch import helpers


# def IH_logger(OT_INPUT, HANDLINGS, PORT, MODSETTINGS, LOGS):
def main(HANDLINGS, PORT, LOGS, SETTINGS, module_name):
	'''
	#FIXME
	'''
	#INITIALISATION
	LOGS.append(f"==== {module_name}  ====")


	#ECRITURE
	for to_log in SETTINGS["OT_input"]["logging"]:
		es = Elasticsearch(to_log["options"][0]["value"])
		data = [
			{
				"_index": to_log["options"][1]["value"],
				"doc": {
					"body": str(datum)
				}
			} 
			for datum in LOGS
		]
		helpers.bulk(es, data)


	#CLOTURE
	#LOGS.append(f"====> {module_name} ENDS <====")
	return (HANDLINGS, PORT, LOGS )


#================================================================
