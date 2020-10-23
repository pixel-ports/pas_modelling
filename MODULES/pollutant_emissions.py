# from datetime import datetime 
# from datetime import timedelta
import datetime #Contrainte pr les tests de type


def main(HANDLINGS, PORT, LOGS, SETTINGS, module_name) : #TODO manque l'utilisation d'emission factor spécifiques
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
				for energy_ID, energy_consumption in resource_outcome["Energy_consumptions"].items():
					success, data = get_default_pollutant_emissions(energy_ID, energy_consumption, PORT["energies"])
				if success:
					resource_outcome.update({"Pollutant_emissions": data})
				else:
					Invalide_handlings.append(handling)
					Errors_details.append(data)


	#CLOTURE
	LOGS.append(f"Number of handlings for which activities's pollutant emissions could not be established: {len(Invalide_handlings)}") #Impacte l'assignation a travers l'affectation de l'ordre des SC résultantes
	if len(Invalide_handlings) > 0:
		LOGS.append({"List of discarted handling and detailstails" : list(zip(Invalide_handlings, Errors_details))}) #TODO remettre au propres, uniformiser la manière de faire ds les différents modules

	return HANDLINGS, PORT, LOGS

#=====================================================
def get_default_pollutant_emissions(energy_ID:str, energy_consumption:dict, ENERGIES:dict)-> tuple:
	success = None
	data = {}

	try:
		for pollutant_ID, pollutant_emissionFactor in ENERGIES[energy_ID]["emissionFactors"].items():
			data.update({pollutant_ID:{
				"amount": pollutant_emissionFactor["Value"] * energy_consumption["amount"],
				"unit": pollutant_emissionFactor["Unit"][:-2] #TODO controle l'unité (analyse dimensionnelle)
			}})
			success = True
	except Exception as error:
		success = False
		data = error

	return success, data

def get_specific_pollutant_emissions(energy_ID:str, energy_consumption:dict, ressource:dict)-> tuple:
	pass #TODO
	'''
	#emission_factor specifiques à la ressource
		if ressource.get("emissions", {}).get() != "missing":
			for pollutant, emission_factor in ressource["emissions"].items():
				data.update({pollutant:{
					"amount": emission_factor["value"] * (activity['duration'].total_seconds() / (60*60)),
					"unit": emission_factor["unit"]
				}})
	'''