import json
from elasticsearch import Elasticsearch
from elasticsearch import helpers


def main(LOGS=None, HANDLINGS=None, export_infos=None, abording=False, target='IH'):
	'''
	'''
	LOGS.append(f"==== Outputs exporter ====")
	material = {
		"atomic_handlings":HANDLINGS,
		#"PAS_tree":convert_to_tree(HANDLINGS),#FIXME
		"internalLog":LOGS
	}
	if target == "IH":
		for output in export_infos: 
			request_arg = {option["name"]:option["value"] for option in output["options"]}
			put_IH(material=material[output["name"]], type=output["type"], arg=request_arg)
	

	if target == "local files":
		if abording:
			message = f"Crashed, last log: {LOGS[-1]}"
			LOGS.append(message)
			print(message)
		LOGS.append(f"PAS outputs export to local files before closing")
		folder = "./OUTPUTS/"
		exports = {
			"PAS": convert_to_tree(HANDLINGS),
			"atomic_handlings": HANDLINGS,
			"internalLog": LOGS,
			#"PAS_instance" : PAS_instance
		}
		for title, content in exports.items():
			file_path = folder + title + ".json"
			with open(file_path, 'w') as file:
				json.dump(content, file, indent=4, default=str)
			print(f"{title} exported in {file.name}")
		print(f"\nClosing. Bye")
		# if abording:
		# 	sys.exit(1)
#================================================================
def put_IH(material, type, arg): #TODO ajouter retour requet TODO vérifier format TS
	es = Elasticsearch(arg["url"])
	data = [
		{
			"_index": arg["recipientId"],
			"doc": json.dumps(datum, indent=4, default=str)
		} for datum in material
	]
	helpers.bulk(es, data)

def convert_to_tree(HANDLINGS):
	pass #FIXME