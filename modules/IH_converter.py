import json
import jsonschema
import logging
import datetime
#import dateutil.parser

logger = logging.getLogger("IH_converter")


def IH_converter(inputs, modSettings) :
	'''
	Transform previous PAS state into proper Handlings
	'''
	logger.warning("Starting")

	# CHECK INPUT

	# PROCESSING
	output = {} # Plutôt que d'opérer sur l'objet inputs, je préfère travailler un autre (choix discutable)
	output["parameters"] = inputs["parameters"]
	output["handlings"] = []
	output["rejected_handlings"] = {
		"invalid_key":{
			"direction":[],
			"amount":[],
			"status":[]
			}
		}
	handling_counter = 0
	
	for handling in inputs["handlings"][0]["records"]:
		#TODO mettre un try de validation contre le schema. Si échec, identifier la (première) clé problématique et mettre dans les rejetés correspondants (on garde le get(None pr les champs non critiques))
		#TODO le format de date n'est pas le bon (cf fonction)
		if handling["data"]["operation"] in ["loading", "unloading"] :
			direction = handling["data"]["operation"]
			output["handlings"].append(
				{
					"content_agent":		handling["data"].get(direction + "_agent", None),
					"content_amount":		handling["data"].get(direction + "_tonnage", None),
					"content_dangerous":	handling["data"].get(direction + "_dangerous", None),
					"content_label":		None,
					"contents_type":		handling["data"].get(direction + "_cargo_type", None),
					"handling_direction":   handling["data"].get("operation", None),
					"handling_dock":		str(handling["data"].get(direction + "_berth", None)),
					"handling_ID": 			"handling_" + str(handling_counter),
					"handling_maxEnd":		timeConvert(handling["data"].get("departure_dock", None)), 
					"handling_minStart":	timeConvert(handling["data"].get("arrival_dock", None)), #Sera affiné par Availability_calculator si activé dans le service.
					"handling_operator": 	handling["data"].get("operator", None),
					"handling_type": 		handling["data"].get(direction + "_cargo_fiscal_type", None),
					"ship_capacity":		None,
					"ship_ID":				str(handling["data"].get("IMO", None)),
					"ship_label": 			handling["data"].get("name", None),
					"ship_type": 			None,
					"stopover_ETA": 		timeConvert(handling["data"].get("arrival_dock", None)),
					"stopover_ETD": 		timeConvert(handling["data"].get("departure_dock", None)),
					"stopover_ID":			str(handling["data"].get("journeyid", None)),
					"stopover_status": 		None, #TODO inférer valeur d'après les champs présent
					"stopover_terminal": 	None
				}
			)
		else :
			output["rejected_handlings"]["invalid_key"]["handling_direction"].append(handling["data"])

		# ts1 = output["handlings"][0]["ship_ETA"] 
		# ts2= output["handlings"][0]["ship_ETD"]
		# som2=datetime.date.today()+ datetime.timedelta(days=2)
		# type(som2)
		# somme = ts1 + datetime.timedelta(days=2)

		# out1=datetime.datetime.utcfromtimestamp(ts1/1000).isoformat()
		# out2= datetime.datetime.utcfromtimestamp(ts2/1000).isoformat()
		# out3=datetime.datetime.utcfromtimestamp(somme/1000).isoformat() 
		handling_counter += 1

	#juste pr check
	with open("./export_IH_converter.json", "w") as file :
	    #Attention, necessite de convertir les datetime en iso avant
		json.dump(output, file)

	# CHECK OUTPUT
	logger.warning("Ending")
	return output

def timeConvert(epoch_timestamp):
	#FIXME c'est moche
	try : 
		datetime.datetime.utcfromtimestamp(epoch_timestamp/1000)#.isoformat()
	except :
		return None
	else:
		return datetime.datetime.utcfromtimestamp(epoch_timestamp/1000).isoformat()
		#return epoch_timestamp #Pr tests en epoch

