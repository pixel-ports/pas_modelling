import json
import jsonschema
import logging
import datetime

logger = logging.getLogger("IH_converter")


def IH_converter(HANDLINGS, PORT, LOGS, SETTINGS, name) :
	'''
	Transform  raw stopover data into proper handlings request.
	'''
	logger.warning("Starting")

	#INITIALISATION
	Unconverted_records = []
	
	# CONVERTION DES CHAMPS
	HANDLINGS = [stopover_converter(stopover, HANDLINGS.index(stopover))
		for stopover in HANDLINGS 
		if stopover["operation"] in ["loading", "unloading"]
	]

	handling_counter = 0
	for stopover in HANDLINGS:
		try:
			stopover = stopover_converter(stopover, handling_counter)
			handling_counter += 1
		except:
			Unconverted_records.append(stopover)
		else:
			Unconverted_records
	
	#vérifier qu'en sortie len(HANDLINGS) == handling_counter et que len(HANDLINGS)+len(discarded_handling)
	LOGS.append(f"{handling_counter} records succeffully converted, {len(Unconverted_records)} record discarded ({len(Unconverted_records) / len(HANDLINGS)} %)") #FIXME crachera si 0 handlings

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
	# for stopover in HANDLINGS:

	HANDLINGS = [handling for handling in HANDLINGS if (
		handling["content_amount"]>0
		and handling["content_type"]!="" #VARIANTE (drastique): in [rule_content_type["content_type_ID"] for rule_content_type in PAS["parameters"]["RULES"]["content_type_list"]]
		and handling["handling_direction"] in ["loading", "unloading"]
		and handling["handling_dock"]!=""
		#and handling["handling_minStart"] < handling["handling_maxEnd"] #FIXME "'<' not supported between instances of 'datetime.datetime' and 'NoneType'"
		and handling["handling_type"]!="" 
		#and handling["stopover_ETA"] < handling["stopover_ETD"]
	)]

	

	# logger.warning("Ending")
	return (HANDLINGS, PORT, LOGS, SETTINGS)


#=========================================================================
def stopover_converter(stopover, counter):
	'''Convert one IH's stopover record (combined forced loading and unloading) into proper handling, with a key selection based on 'operation' value
	NB: for a real dual stopover (unloading AND loading), only the one corresponding to the 'operation' value will be converted to handling ! #FIXME: à voir avec DAL/IH
	'''
# if stopover["operation"] in ["loading", "unloading"] :
	return {
		"content_agent":			stopover.get(stopover["operation"] + "_agent"),
		"content_amount":			stopover.get(stopover["operation"] + "_tonnage"),
		"content_dangerous":		stopover.get(stopover["operation"] + "_dangerous"),
		"content_label":			None,
		"content_type":				stopover.get(stopover["operation"] + "_cargo_type"),
		"handling_direction":   	stopover.get("operation"),
		"handling_dock":			str(stopover.get(stopover["operation"] + "_berth")),
		"handling_ID": 				"handling_" + str(counter),
		"handling_lattestEnd":		timeConvert(stopover.get("arrival_dock")), #Suivant le sens réel de stopover_ETD, peut nécessiter de soustraire journey_duration(handling) 
		"handling_earliestStart":	timeConvert(stopover.get("departure_dock")), #Cf stopover_ETA
		"handling_operator": 		stopover.get("operator"),
		"handling_type": 			stopover.get(stopover["operation"] + "_cargo_fiscal_type"),
		"ship_capacity":			None,
		"ship_ID":					str(stopover.get("IMO")),
		"ship_label": 				stopover.get("name"),
		"ship_type": 				None,
		"stopover_ETA": 			timeConvert(stopover.get("arrival_dock")), #Dans le cas des données consolidées pr GPMB, c'est en fait le timestamp d'arrivée à quai. Mais peut être le TS vis à vis du port pr d'autres cas.
		"stopover_ETD": 			timeConvert(stopover.get("departure_dock")), #Cf stopover_ETA
		"stopover_ID":				str(stopover.get("journeyid")),
		"stopover_status": 			None, #TODO inférer valeur d'après les champs présent
		"stopover_terminal": 		str(stopover.get("source"))
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
