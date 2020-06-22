# from datetime import datetime 
# from datetime import timedelta
import datetime #Contrainte pr les tests de type
from itertools import groupby

def main(HANDLINGS, PORT, LOGS, SETTINGS, module_name) :
	'''
	For each activity, resolve the energies consumptions.
	NB: 1 activity --> N energies (1 consumption for each)
	'''
	#PRINCIPLE
	# ∀ handling
	# 	∀ activity
	# 		∀ resource
	# 			retrive resource_consumption
				# ∀ energy
	# 				resolve consumption
	# 		resolve_total(Resources)
	# 	resolve_total(Activities)
	# resolve_total(Handlings)	
	
	#INITIALIZATION
	LOGS.append(f"==== {module_name}  ====")
	#	SOME LIST	
	Invalide_handlings = [] #Pr les logs
	Errors_details = [] #Pr les logs

	
	#PROCESSING
	for handling in HANDLINGS:
		
		#DETAILLED CONSUMPTION
		for activity in handling["Activities"]:

			success, data = get_energies_consumptions(activity, PORT["Resources"])
			if success:
				activity["Resources_uses"] = data
				del activity['Resources_IDs']
			else:
				Invalide_handlings.append(handling)
				Errors_details.append(data)
				
			
		# AGREGATED ENERGIES CONSUMPTIONS TODO refactoriser, mais attention à l'indentation
			success, data = sum_energies_consumptions(activity["Resources_uses"])
			if success:
				activity["Energies_consumptions"] = data
		
		success, data = sum_energies_consumptions(handling["Activities"])
		if success:
			handling["Energies_consumptions"] = data
	
	# success, data = sum_energies_consumptions(HANDLINGS) #TODO ajouter une entrée pr somme globale sur le PAS
	# if success:
	# 	PAS["Energies_consumptions"] = data
	
	
	#CLOTURE
	LOGS.append(f"Number of handlings for which activities could not be established: {len(Invalide_handlings)}") #Impacte l'assignation a travers l'affectation de l'ordre des SC résultantes
	if len(Invalide_handlings) > 0:
		LOGS.append({"List of discarted handling and detailstails" : list(zip(Invalide_handlings, Errors_details))})
	#LOGS.append(f"====> {module_name} ENDS <====")
	return HANDLINGS, PORT, LOGS, SETTINGS

#=====================================================
def get_energies_consumptions(activity, Resources):
	success = False
	data = []

	try:
		Resources_descriptions = [resource for resource in Resources["machines"] if resource["ID"] in activity["Resources_IDs"]]
		for resource in Resources_descriptions : #NB on choisit d'avoir la granularité la plus fine (donc pr chaque machine, on fera les aggrégations après)
			data.append({
				"resource_ID": resource["ID"],
				"Energies_consumptions":[{
					"energy_ID": energy['nature'],
					"amount": energy["value"] * (activity['duration'].total_seconds() / 60),
					"unit": energy["unit"]
				} for energy in resource['consumptions']]
			})

		success = True


	except Exception as error:
		data = error


	return success, data


def sum_energies_consumptions(Childrens):
	success = False
	data = []

	try:
		temp_Total = {}
		Consumptions = [consumption 
			for children in Childrens
			for consumption in children["Energies_consumptions"]
		]
		for consumption in Consumptions: #On s'embête à cause de la possibilité qu'un user rentre une énergie custom qui ait le même nom qu'une autre (ex electricity) mais une unité différentes
			temp_Total.setdefault((consumption["energy_ID"], consumption["unit"]), consumption["amount"])
			temp_Total[(consumption["energy_ID"], consumption["unit"])] += consumption["amount"]
		
		for energy_unit, amount in temp_Total.items():
			data.append({
				"energy_ID": energy_unit[0],
				"amount": amount,
				"unit":energy_unit[1]
			})

		success = True
		

	except Exception as error:
		success = False
		data = error


	return success, data