import json
import jsonschema
import datetime


def process(HANDLINGS, PORT, LOGS, SETTINGS, name) :
	'''
	Transform  raw stopover data into proper handlings request.
	'''
	#INITIALISATION
	LOGS.append(f"===== {name} STARTS =====")


	# CONVERTION DES CHAMPS
	Converted_records = []
	Unconverted_records = []
	for record in HANDLINGS:
		convertion_success, convertion_object = stopover_converter(record, len(Converted_records))
		if convertion_success:
			Converted_records.append(convertion_object)
		elif not convertion_success:
			Unconverted_records.append(record)
	
	LOGS.append(f"Convertion: {len(HANDLINGS)} records where passed, {len(Converted_records)} records succeffully converted, {len(Unconverted_records)} record discarded")
	LOGS.append({"Discarted records": Unconverted_records})
	HANDLINGS = Converted_records
	
	
	# FILTRATION 
	Suitable_records = []
	Unsuitable_records = []
	for record in HANDLINGS:
		filtering_success, filtering_Messages = handling_filter(record, SETTINGS["modules_settings"][name]["filters"])
		if filtering_success:
			Suitable_records.append(record)
		else :
			Unsuitable_records.append({"record": record, "causes": filtering_Messages })
	
	LOGS.append(f"Filtration: {len(HANDLINGS)} records where passed, {len(Suitable_records)} records suitable, {len(Unsuitable_records)} records discarded")
	LOGS.append({"Discarted records": Unsuitable_records})
	HANDLINGS = Suitable_records
	

	
		
	#CLOSSING
	LOGS.append(f"===== {name} ENDS =====")
	return (HANDLINGS, PORT, LOGS, SETTINGS)


#=========================================================================
def stopover_converter(stopover, ID_number):
	'''Convert one IH's stopover record (combined forced loading and unloading) into proper handling, with a key selection based on 'operation' value
	NB: for a real dual stopover (unloading AND loading), only the one corresponding to the 'operation' value will be converted to handling ! #FIXME: à voir avec DAL/IH
	'''
	try:
		handling = {
			"content_agent":			str(stopover.get(stopover["operation"] + "_agent")),
			"content_amount":			int(stopover.get(stopover["operation"] + "_tonnage")),
			"content_dangerous":		bool(stopover.get(stopover["operation"] + "_dangerous")),
			"content_label":			None,
			"content_type":				str(stopover.get(stopover["operation"] + "_cargo_type")),
			"handling_direction":   	str(stopover.get("operation")),
			"handling_dock":			str(stopover.get(stopover["operation"] + "_berth")),
			"handling_ID": 				"handling_" + str(ID_number),
			"handling_lattestEnd":		timeConvert(stopover.get("arrival_dock")), #Suivant le sens réel de stopover_ETD, peut nécessiter de soustraire journey_duration(handling) 
			"handling_earliestStart":	timeConvert(stopover.get("departure_dock")), #Cf stopover_ETA
			"handling_operator": 		str(stopover.get("operator")),
			"handling_type": 			str(stopover.get(stopover["operation"] + "_cargo_fiscal_type")),
			"ship_capacity":			None,
			"ship_ID":					str(stopover.get("IMO")),
			"ship_label": 				str(stopover.get("name")),
			"ship_type": 				None,
			"stopover_ETA": 			timeConvert(stopover.get("arrival_dock")), #Dans le cas des données consolidées pr GPMB, c'est en fait le timestamp d'arrivée à quai. Mais peut être le TS vis à vis du port pr d'autres cas.
			"stopover_ETD": 			timeConvert(stopover.get("departure_dock")), #Cf stopover_ETA
			"stopover_ID":				str(stopover.get("journeyid")),
			"stopover_status": 			None, #TODO inférer valeur d'après les champs présent
			"stopover_terminal": 		str(stopover.get("source"))
		}
		success = True
	except:
		handling = stopover
		success = False
	return success, handling

def handling_filter(handling, enabled_filters):
	''' 
	Check si un ensemble de contions sont respectées par l'handling. Renvois le status et une liste de message.
	NB: 
	- on pourrait couvrir une bonne partie des besoins avec un simple test contre un json-schema, mais pas les plus complexes.
	- on pourrait distinguer les causes de warning et les causes de discart du handling
	- plusieures conditions pourraient être à rajouter, mais cela dépends du contexte (ouvre la voie à des paramètres pr cette fonctions, qui seraient tirés des settings de ce module (fixés pr ce port)
	'''
	Messages = []
	if enabled_filters["content_amount"] :
		if handling["content_amount"] <= 0 :
			Messages.append(f"Content amount should be > 0")
	if enabled_filters["content_type"] :
		if handling["content_type"] == "" or handling["content_type"] == None: #VARIANTE (drastique): in [rule_content_type["content_type_ID"] for rule_content_type in PAS["parameters"]["RULES"]["content_type_list"]]
			Messages.append(f"Content type should be provided")
	if enabled_filters["handling_direction"] :
		if handling["handling_direction"] not in ["loading", "unloading"] :
			Messages.append(f"Handling direction should be loading or unloading") #FIXME ne marchera pas pour les paquebots etc
	if enabled_filters["handling_dock"] :
		if handling["handling_dock"] == "" or  handling["handling_dock"] == None:
			Messages.append(f"Dock should be provided") #VARIANTE (drastique) : Restreindre à être dans la liste d'ID de dock ? (cf conten_type)
	if enabled_filters["ET_consistency"] :
		if handling["stopover_ETA"] is not None and handling["stopover_ETD"] is not None :
			if handling["stopover_ETA"] > handling["stopover_ETD"]:
				Messages.append(f"ETA should be before ETD")
	# - content type référencé (simple warning cause géré par default_SC)
	# - handling type référencé
	# - dock référencé
	# - pas de doublons
	# - content et handling type cohérents
	# - amount cohérent capacité
	# - check contre un schéma ?

	if len(Messages) > 0:
		success = False
	else:
		Messages.append("Record filtering: successfull")
		success = True
	return success, Messages

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
