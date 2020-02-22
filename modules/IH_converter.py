import json
import jsonschema
import logging
import datetime

logger = logging.getLogger("IH_converter")


def IH_converter(pas, module_settings) :
	'''
	Transform stopover_seed into proper Handlings
	'''
	logger.warning("Starting")

	handlings = []
	handling_counter = 0
	log= {
		"rejected_handlings": {
			"invalid_key" : {
				"direction":[],
				"amount":[],
				"status":[]
			}
		}
	}


	# PROCESSING
	for stopover in pas["state"]:
		handling_counter += 1 #C'est un ID qui peut apparaitre à l'utilisateur ==> on commence à 1
		if stopover["operation"] in ["loading", "unloading"] :
			handlings.append(transmutStopovers(stopover, handling_counter))
		else :
			log["rejected_handlings"]["invalid_key"]["handling_direction"].append(stopover)


	# FILTRATION #TODO
		# - content type référencé
		# - handling type référencé
		# - doc référencé
		# - content et handling type cohérents
		# - sortie postérieur entrée
		# - amount cohérent capacité

	# CHECK OUTPUT
	pas["state"] = handlings
	pas["log"]["IH_converter"] = log 

	logger.warning("Ending")
	return pas

def transmutStopovers(stopover, counter):
	#FIXME Quid des stopovers avec 2 handlings incorporés ? est ce que le stopover a été doublé dans l'IH? ou alors autre clé que loading OU unloading?
	#TODO mettre un try de validation contre le schema. Si échec, identifier la (première) clé problématique et mettre dans les rejetés correspondants (on garde le get(None pr les champs non critiques))
	direction = stopover["operation"]
	handling = {
		"content_agent":		stopover.get(direction + "_agent", None),
		"content_amount":		stopover.get(direction + "_tonnage", None),
		"content_dangerous":	stopover.get(direction + "_dangerous", None),
		"content_label":		None,
		"content_type":			stopover.get(direction + "_cargo_type", None),
		"handling_direction":   stopover.get("operation", None),
		"handling_dock":		str(stopover.get(direction + "_berth", None)),
		"handling_ID": 			"handling_" + str(counter),
		"handling_maxEnd":		timeConvert(stopover.get("departure_dock", None)), 
		"handling_minStart":	timeConvert(stopover.get("arrival_dock", None)), #Sera affiné par Availability_calculator si activé dans le service.
		"handling_operator": 	stopover.get("operator", None),
		"handling_type": 		stopover.get(direction + "_cargo_fiscal_type", None),
		"ship_capacity":		None,
		"ship_ID":				str(stopover.get("IMO", None)),
		"ship_label": 			stopover.get("name", None),
		"ship_type": 			None,
		"stopover_ETA": 		timeConvert(stopover.get("arrival_dock", None)),
		"stopover_ETD": 		timeConvert(stopover.get("departure_dock", None)),
		"stopover_ID":			str(stopover.get("journeyid", None)),
		"stopover_status": 		None, #TODO inférer valeur d'après les champs présent
		"stopover_terminal": 	None
		}
	return handling 

def timeConvert(epoch_timestamp, output_format = 'datetime_obj'):
	'''
	3 formats de sortie possible : 'datetime_obj' (défaut), 'str_iso' (pr export json), keep_epoch
	'''
	#FIXME le format de date n'est pas le bon?
	try : 
		datetime.datetime.utcfromtimestamp(epoch_timestamp/1000)
	except TypeError:
		return None
	else:
		if output_format == 'str_iso' :
			return datetime.datetime.utcfromtimestamp(epoch_timestamp/1000).isoformat()
		if output_format == 'datetime_obj' :
			return datetime.datetime.utcfromtimestamp(epoch_timestamp/1000)
		if output_format == 'keep_epoch' :
			return epoch_timestamp