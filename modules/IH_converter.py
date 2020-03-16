import json
import jsonschema
import logging
import datetime

logger = logging.getLogger("IH_converter")


def IH_converter() :
	'''
	Transform IH's stopover data into proper handlings request.
	'''
	# logger.warning("Starting")

	handlings = []
	handling_counter = 0

	# CONVERTION DES CHAMPS
	for stopover in STATE:
		handling_counter += 1
		try:
			stopover_converter(stopover, handling_counter)
			LOGS.append(f"IH_converter: successfully converted stopover {stopover}")
			logger.warning(f"IH_converter: successfully converted stopover {stopover}")
		except:
			logger.warning(f"IH_converter: issue on convertion for stopover {stopover}")
			LOGS.append(f"{
				"issue": {
					'invalid_key': {
						"key":"handling_direction",
						"value":stopover["operation"],
						"comment": "Should be equal to loading or unloading"
					}
				},
				"module":"IH_converter",
				"item": stopover
			})


	# FILTRATION 
	#TODO
	# - content type référencé (simple warning cause géré par default_SC)
	# - handling type référencé
	# - dock référencé
	# - pas de doublons
	# - content et handling type cohérents
	# - sortie postérieur entrée
	# - amount cohérent capacité
	# - check contre un schéma ?
	temp_filtre_handlings = [handling for handling in handlings if (
		handling["content_amount"]>0
		and handling["content_type"]!="" #VARIANTE (drastique): in [rule_content_type["content_type_ID"] for rule_content_type in PAS["parameters"]["RULES"]["content_type_list"]]
		and handling["handling_direction"] in ["loading", "unloading"]
		and handling["handling_dock"]!=""
		#and handling["handling_minStart"] < handling["handling_maxEnd"] #FIXME "'<' not supported between instances of 'datetime.datetime' and 'NoneType'"
		and handling["handling_type"]!="" 
		#and handling["stopover_ETA"] < handling["stopover_ETD"]
	)]

	PAS["state"] = temp_filtre_handlings #handlings

	# logger.warning("Ending")
	return PAS


#=========================================================================
def stopover_converter(stopover, counter):
	'''Convert one IH's stopover record (combined forced loading and unloading) into proper handling, with a key selection based on 'operation' value
	NB: for a real dual stopover (unloading AND loading), only the one corresponding to the 'operation' value will be converted to handling ! #FIXME: à voir avec DAL/IH
	'''
	if stopover["operation"] in ["loading", "unloading"] :
		return {
			"content_agent":		stopover.get(stopover["operation"] + "_agent", None),
			"content_amount":		stopover.get(stopover["operation"] + "_tonnage", None),
			"content_dangerous":	stopover.get(stopover["operation"] + "_dangerous", None),
			"content_label":		None,
			"content_type":			stopover.get(stopover["operation"] + "_cargo_type", None),
			"handling_direction":   stopover.get("operation", None),
			"handling_dock":		str(stopover.get(stopover["operation"] + "_berth", None)),
			"handling_ID": 			"handling_" + str(counter),
			"handling_lattestEnd":		timeConvert(stopover.get("departure_dock", None)), #Suivant le sens réel de stopover_ETD, peut nécessiter de soustraire journey_duration(handling) 
			"handling_earliestStart":	timeConvert(stopover.get("arrival_dock", None)) + journey_duration(stopover) + inspection_duration(stopover), #Cf stopover_ETA
			"handling_operator": 	stopover.get("operator", None),
			"handling_type": 		stopover.get(stopover["operation"] + "_cargo_fiscal_type", None),
			"ship_capacity":		None,
			"ship_ID":				str(stopover.get("IMO", None)),
			"ship_label": 			stopover.get("name", None),
			"ship_type": 			None,
			"stopover_ETA": 		timeConvert(stopover.get("arrival_dock", None)), #Dans le cas des données consolidées pr GPMB, c'est en fait le timestamp d'arrivée à quai. Mais peut être le TS vis à vis du port pr d'autres cas.
			"stopover_ETD": 		timeConvert(stopover.get("departure_dock", None)), #Cf stopover_ETA
			"stopover_ID":			str(stopover.get("journeyid", None)),
			"stopover_status": 		None, #TODO inférer valeur d'après les champs présent
			"stopover_terminal": 	str(stopover.get("source", None))
		}



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


def journey_duration(stopover): #Ajouter en argument les paramètres (Rules)
    '''
    
    '''
    journey_delta = datetime.timedelta(hours=0) #FIXME Si le quai de déstination du bateau est parmi [A, B, C], alors le delais de transit jusqu'au quai est de...

    return journey_delta


def inspection_duration(stopover): #Ajouter en argument les paramètres (Rules)
    '''
    
    '''
    inspection_duration_delta = datetime.timedelta(hours=0) #FIXME Si le type de cargaison est parmi [A, B, C], alors le delais d'inspection est de ...
    
    return inspection_duration_delta