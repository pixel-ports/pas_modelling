# from datetime import datetime 
# from datetime import timedelta
import datetime #Contrainte pr les tests de type


def main(HANDLINGS, PORT, LOGS, SETTINGS, module_name) : #TODO manque l'agrégation (dépend de la conversion du PAS à un arbre)
	'''
	For each activity, resolve the energies consumptions.
	NB: 1 activity --> N energies (1 consumption for each)
	'''
	#INITIALIZATION
	LOGS.append(f"==== {module_name}  ====")
	Invalide_handlings = [] #Pr les logs
	Errors_details = [] #Pr les logs

	
	#PROCESSING
	for handling in HANDLINGS:
		for activity in handling["Activities"]:
			for resource_ID, resource_outcome in activity['Resources_used'].items():
				success, data = get_energies_consumptions(activity, PORT["resources"][resource_ID])
			if success:
				resource_outcome.update({"Energy_consumptions": data})
			else:
				Invalide_handlings.append(handling)
				Errors_details.append(data)


	#CLOTURE
	LOGS.append(f"Number of handlings for which activities's energy consumptions could not be established: {len(Invalide_handlings)}") #Impacte l'assignation a travers l'affectation de l'ordre des SC résultantes
	if len(Invalide_handlings) > 0:
		LOGS.append({"List of discarted handling and detailstails" : list(zip(Invalide_handlings, Errors_details))}) #TODO remettre au propres, uniformiser la manière de faire ds les différents modules

	return HANDLINGS, PORT, LOGS

#=====================================================
def get_energies_consumptions(activity: dict, res:dict)-> tuple:
	success = None
	data = {}

	try:
		for energy, consumption in res["consumptions"].items():
			data.update({energy:{
				"amount": consumption["value"] * (activity['duration'].total_seconds() / (60*60)),
				"unit": consumption["unit"]
			}})
		success = True
	except Exception as error:
		success = False
		data = error

	return success, data
