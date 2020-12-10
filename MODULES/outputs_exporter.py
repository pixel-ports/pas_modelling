import json
from elasticsearch import Elasticsearch
from elasticsearch import helpers


def main(export_infos=None, LOGS=None, HANDLINGS=None, ):
	'''
	'''
	LOGS.append(f"==== Outputs exporter ====")
	outputs = {
		"handlings":HANDLINGS,
		#"PAS_tree":convert_to_tree(HANDLINGS),#FIXME
		"logs":LOGS
	}
	for export in export_infos: 
		success, data = put_IH(outputs, export)
		LOGS.append(data)
	return LOGS
#================================================================
def put_IH(output_value, export): #TODO ajouter retour requet TODO vérifier format TS
	success = None
	data = None
	try:
		request = {option["name"]:option["value"] for option in export["options"]}
		output = {
			"name":export["name"],
			"type":export["type"],
			"value":output_value
		}
		# if output is not dict:
			# output = {export["name"]:[output]}
		Elasticsearch().index(
            index= request["index_id"], 
            id= request["document_id"], 
            body= json.dumps(output, default=str),
			#headers={'Content-Type': 'application/json'}
        )
		success = True
		data = f'{export["name"]} exported in index {request["index_id"]}, document {request["document_id"]}'
	except Exception as error:
		success = False
		data = error
	return success, data