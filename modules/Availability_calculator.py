# import json
# import jsonschema
# import logging
import datetime

# logger = logging.getLogger("Availability_calculator")


# def process(pas, module_settings) :
def process(HANDLINGS, PORT, LOGS, SETTINGS, name):
	'''
	Infer handling earliest possible TS for begining processing
	'''
	# logger.warning("Starting")

	#INITIALISATION
	LOGS.append(f"===== {name} STARTS =====")


	# PROCESSING
	for handling in pas["state"]: #TODO factoriser les 2 cas
		# Disponnible au plus tôt
		try :
			handling["handling_minStart"] = handling["stopover_ETA"] + journey_duration(handling) + inspection_duration(handling) #On doit pouvoir raisonnablement se limiter à un try sur handling["ship_ETA"]
		except :
			pass #FIXME (vérifier si d'autres cas) la clé n'existait pas, à la convertion on choisit de mettre en valeur None ==> TypeError unsupported operand type(s) for -: 'NoneType' and 'datetime.timedelta'
		else :
			handling["handling_minStart"] = handling["stopover_ETA"] + journey_duration(handling) + inspection_duration(handling)
		# Doit terminer au plus tard
		try :
			handling["handling_maxEnd"] = handling["stopover_ETD"] - journey_duration(handling) - inspection_duration(handling)
		except :
			pass
		else :
			handling["handling_maxEnd"] = handling["stopover_ETD"] - journey_duration(handling) - inspection_duration(handling)
# "handling_lattestEnd":		timeConvert(stopover.get("departure_dock", None)), #Suivant le sens réel de stopover_ETD, peut nécessiter de soustraire journey_duration(handling) 
# "handling_earliestStart":
# Vérifier aussi cohérence chronologie
# "handling_lattestEnd":		timeConvert(stopover.get("departure_dock", None)), #Suivant le sens réel de stopover_ETD, peut nécessiter de soustraire journey_duration(handling) 
# 		"handling_earliestStart":	timeConvert(stopover.get("arrival_dock", None)) + journey_duration(stopover) + inspection_duration(stopover), #Cf stopover_ETA


	#CLOTURE
	LOGS.append(f"===== {name} ENDS =====")
	return (HANDLINGS, PORT, LOGS, SETTINGS)


#================================================================
def journey_duration(item):
	'''
	Si le quai de déstination du bateau est parmi [A, B, C], alors Avail_TS = ETA + x...
	Pas de prise en compte de l'heure (marées etc)
	'''
	journey_delta = datetime.timedelta(hours=0) #TODO

	return journey_delta

def inspection_duration(item):
	'''
	Si le type de cargaison est parmi [A, B, C], alors Avail_TS = ETA + x...
	Pas de prise en compte de l'heure (heure de travail)
	'''
	inspection_duration_delta = datetime.timedelta(hours=0) #TODO
	
	return inspection_duration_delta