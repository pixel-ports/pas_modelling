import json
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import datetime


def main(PAS_instance=None, LOGS=None, HANDLINGS=None, local_export=False):
	'''
	'''
	LOGS.append(f"==== Outputs exporter ====")
	output_content = {
		"handlings":HANDLINGS,
		"logs":LOGS,
		"pas_instance":json.dumps(PAS_instance)
	}

	for output_call in PAS_instance.get("output", ''):
		success, data = put_IH(output_content, output_call)
		LOGS.append(f"Output exported in IH : {success} ({data})")
	
	if local_export:
		path = "./OUTPUTS/PAS_output.json"
		with open(path, 'w') as file:
			json.dump(output_content, file, indent=4, default=str)
		LOGS.append(f"Output exported localy in file {path}")

	return LOGS
#================================================================
def put_IH(output_content, output_call): #TODO ajouter retour requet TODO vérifier format TS
	success = None
	data = None
	if output_call != '':
		options = {option["name"]:option["value"] for option in output_call["options"]}
	index_id = output_call.get("index_id", '')
	if index_id =='':
		index_id = "pas_default_output"
	doc_id = output_call.get("doc_id", '')
	if doc_id =='':
		doc_id = "unamed"
	document = {
        "info":{
            "ID": doc_id,
            'nature': "output",
            'type': output_call.get("name", ''),
            'format': "unique_document",
            "DM_version": "DMv4.1.3",
            "creation_TS": datetime.datetime.now().timestamp()
        },
        "data":output_content
    }
	try:
		Elasticsearch().index(
            index= index_id, 
            id= doc_id, 
            body= json.dumps(document, default=str),
			#headers={'Content-Type': 'application/json'}
        )
		success = True
		data = f'index: {index_id}, document: {doc_id}'
	except Exception as error:
		success = False
		data = error
	return success, data