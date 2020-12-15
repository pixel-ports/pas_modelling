import json
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import datetime


def main(export_settings=None, LOGS=None, HANDLINGS=None):
	'''
	'''
	LOGS.append(f"==== Outputs exporter ====")
	output = {
		"handlings":HANDLINGS,
		#"PAS_tree":convert_to_tree(HANDLINGS),#FIXME
		"logs":LOGS
	}
	for export in export_settings:
		success, data = put_IH(output, export)
		LOGS.append(data)
	return LOGS
#================================================================
def put_IH(output_value, export): #TODO ajouter retour requet TODO vérifier format TS
	success = None
	data = None
	export.update({option["name"]:option["value"] for option in export["options"]})
	index_id = export.get("index_id", '')
	if index_id =='':
		index_id = "pas_default_output"
	doc_id = export.get("doc_id", '')
	if doc_id =='':
		doc_id = "unamed"
	document = {
        "info":{
            "ID": doc_id,
            'nature': "output",
            'group': export.get("name", "Unknown"),
            'type': "Logs + handlings",
            'format': "unique_document",
            "DM_version": "DMv4.1.3",
            "creation_TS": datetime.datetime.now().timestamp()
        },
        "data":output_value
    }
	try:
		Elasticsearch().index(
            index= index_id, 
            id= doc_id, 
            body= json.dumps(document, default=str),
			#headers={'Content-Type': 'application/json'}
        )
		success = True
		data = f'Output exported in index: {index_id}, as document: {doc_id}'
	except Exception as error:
		success = False
		data = error
	return success, data