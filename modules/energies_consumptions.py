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
	# 			groupby energy_type with sum
	
	#INITIALIZATION
	LOGS.append(f"<==== {module_name} STARTS ====>")
	#	SOME LIST	
	Invalide_handlings = [] #Pr les logs
	Errors_details = [] #Pr les logs

#---------------------------------------------------------
	handling_ss_duration = []
	for handling in HANDLINGS:
		for activity in handling['activities'].items():
			if activity[1].get("duration") == None:
				handling_ss_duration.append({
					"handling ID": handling["handling_ID"],
					"operation ss durée ID": activity[0],
					# "operation ss durée desc": activity[1]
				})
	#PROCESSING	
	for handling in HANDLINGS:
		for activity_value in handling["activities"].values():
			Resources = [resource for resource in PORT["Resources"]["machines"] if resource["ID"] in activity_value["Resources"]]
			for resources in Resources :
				for energy in resources['consumptions']:
				#FIXME attention à reprendre le formalisme de sortie de la master_v3
					energy_consumption = { #FIXME attention, une machine peut avoir plus d'une énergie ? (ou forcer découpage de la machine en sous-composant ? <== non car à l'inverse on autorise de regrouper des machines !)
						"energy_type": energy['nature'],
						"energy_consumption": energy['value']*2
						# resources[]
					}
			#NB on choisit d'avoir la granularité la plus fine (donc pr chaque machine, on fera les aggrégations après)
	# handling_ss_duration = [handling in HANDLING if handling['activities']['Op_1']['duration']]	
	
	#CLOTURE
	#	Duplicated_content_types
	# LOGS.append(f"Number of handlings for which activities could not be established: {len(Invalide_handlings)}") #Impacte l'assignation a travers l'affectation de l'ordre des SC résultantes
	# if len(Invalide_handlings) > 0:
	# 	Involved_SC = set([handling['Supplychains'][0] #Pas génial de forcer la reprise de la première SC pr avoir la SC utilisée
	# 		for handling in Invalide_handlings
	# 	])
	# 	LOGS.append({f"Supplychains involved {len(Involved_SC)} ({Involved_SC}). List of discarted handling and details": Errors_details})
	LOGS.append(f"====> {module_name} ENDS <====")
	return HANDLINGS, PORT, LOGS, SETTINGS

#=====================================================
def create_HAS(handling:dict, Supplychains_collection: list, Machines_collection: list)-> dict:
	'''Prepare material for operations batch resolution:
	- convert the list of operation to a graph of node (each operation O been split in 2 nodes: 0_start & O_end)
	- initialize some list and variables
	'''
	#TODO les graphes ne devraient pas être recalculés individuellement et à chaque fois ! Tout ce bloc doit être placé en amont (idéalement à la création d'une SC, c'est tout le prb)
	#TODO refaire en faisant une classe. Au lieu d'utiliser des listes, donner un status aux noeuds du graphe
	#TODO a minima, reprendre le formalisme précédent (encapsuler dans un try, sortir le tuple (success/status, data/error))

	#GET SC DATA
	Operations_descriptions = next(
			(port_sc["steps_list"] #Retrieving SC's operation description
			for port_sc in Supplychains_collection #Unretrievable handling's SC already filtered in SC assignation modul
			if port_sc["ID"] == handling["Supplychains"][0]), #Only the operations of the first suitable handling's SC is considered
			None 
		)

	#BUILD GRAPH
	SC_graph = {} 
	for operation in Operations_descriptions:
		#START NODE DEPENDENCIES
		schedule_nature = operation['scheduling']['start']['nature']
		schedule_value = operation['scheduling']['start']['value']
		SC_graph[(operation["ID"], "start")] = [] #Valeur par défaut
		if schedule_nature in ["with_any", "with_all"]:
			SC_graph[(operation["ID"], "start")] = list(set([(parent, "start") for parent in schedule_value]))
		if schedule_nature in ["after_any", "after_all"]:
			SC_graph[(operation["ID"], "start")] = list(set([(parent, "end") for parent in schedule_value]))
			
		#END NODE DEPENDENCIES
		schedule_nature = operation['scheduling']['duration']['nature']
		schedule_value = operation['scheduling']['duration']['value']
		default = [(operation["ID"], "start")] #Valeur par défaut: Toute fin d'opération dépend du début de l'opération (même si le début n'a pas de dépendence, afin de garantir qu'on parcours le graphe entier, condition pour que toutes les opérations soient résolues)
		SC_graph[(operation["ID"], "end")] = default
		if schedule_nature in ["before_any", "before_all"]:
			SC_graph[(operation["ID"], "end")] = list(set(default + [(parent, "start") for parent in schedule_value])) #NB bien inclure le default avant d'appliquer le set()
		if schedule_nature in ["after_any", "after_all"]:
			SC_graph[(operation["ID"], "end")] = list(set(default + [(parent, "end") for parent in schedule_value]))

	#GET MACHINES DATA
	SC_machine_IDs = set([machine_ID 
		for SC in Supplychains_collection
		for operation in SC['steps_list']
		for machine_ID in operation['work']['machines']
	])

	SC_machine_descriptions = [machine
		for machine in Machines_collection
		if machine["ID"] in SC_machine_IDs
	]

	#MERGE ALL INTO A HANDLING ACTIVITIES SCENARIO
	HAS = { #NB On pourrait remplacer par une classe
		#CONTEXTE
		"Operations_descriptions": Operations_descriptions,
		"Machines_descriptions": SC_machine_descriptions,
		"handling_description": handling,
		#GRAPH
		"graph": SC_graph,
		"unchecked":list(SC_graph.keys()),
		"stack": [],
		"checked":[],
		"loop_detected": False,
		#LOGS
		"Logs":[],
		#RESULTS
		"Activities":{}
	} 
	
	return HAS

def wander_HAS(node_ID:str, HAS: dict)-> None:
	'''Recursive function that go accross all the operations graph to:
	- check if there is a dependency loop
	- call for node TS resolution when it's dependencies are resolved.
	NB: there is no return, modifications are affected directly to objects
	'''
	#PARCOURS DE GRAPHE
	HAS["stack"].append(node_ID)
	if HAS["loop_detected"]: #Sortie de la récusion si une boucle a été détectée
		return
	for parent_ID in HAS["graph"][node_ID]:
		if parent_ID in HAS["stack"]: # Détection d'une boucle dans le graphe
			HAS["loop_detected"] = True 
			HAS["error_msg"] = f"Issue for {[node_ID]}: the parent node {parent_ID} creats an infinit loop."
			break
		if parent_ID in HAS["unchecked"]:# Appel récursif sur les dépendences de l'opération
			wander_HAS(parent_ID, HAS)
	
	#RESOLUTION DU NOEUD
	if not HAS["loop_detected"]:
		HAS["unchecked"].remove(node_ID)
		HAS["checked"].append(node_ID) #Le noeud à toutes ces dépendances résolues (y comprit node_start pour un node_end)
		resolve_node(node_ID, HAS) #Le start d'une opération passe forcement en premier, puis le end. On a alors l'entièreté de l'opération qui devient par définition une activitéactivité)

	return #HAS


def resolve_node(node_ID:str, HAS: dict)-> None: #Cette fonction n'est qu'une isolation formelle du bloc de code
	#INITIALIZATION
	operation_description = next((operation_description
		for operation_description in HAS['Operations_descriptions']
		if operation_description["ID"] == node_ID[0]),
		None
	)
	if node_ID[1] == "start":
		key = "start"
	elif node_ID[1] == "end":
		key = "duration" #Dans le DM, l'info pour end est fusionnée avec duration
	schedule_nature = operation_description["scheduling"][key].get("nature")
	schedule_value = operation_description["scheduling"][key].get("value")

	if node_ID[0] not in HAS['Activities']:
		HAS['Activities'][node_ID[0]] = {} #Attention, ici on sort de la structure "usuelle", pas de champs ID mais mais un nom de dict

	HAS['Activities'][node_ID[0]].update({"Ressources": operation_description['work']['machines']}) #On ne l'utilise pas ici, mais plus simple de générer ici pour les modules en aval. 
	
	#CONSTRUCTION DE L'ACTIVITÉ
	#On pourrait séparer en sub fonction distinctes, mais à quoi bon ?
	#NB: on parcours simplement l'arborescence des possibles avec les elif
	#	DELAY (start ou duration)
	if schedule_nature == "delay": 
		if node_ID[1] == "start":#TODO DM maj; plus de delais pr start
			HAS['Activities'][node_ID[0]].update({"start_TS":
				HAS['handling_description']['handling_earliestStart'] + datetime.timedelta(minutes= schedule_value) #NB Attention à l'unité saisie par l'utilisateur
			})
		elif node_ID[1] == "end":
			HAS['Activities'][node_ID[0]].update({"duration": 
				datetime.timedelta(minutes= schedule_value)
			})

	#	DEPENDENCY (start ou end)
	elif schedule_nature in ["before_any", "before_all","with_any", "with_all"]: #Tous pointent vers un start d'opération, mais les before pour générer un end tandis que les with pr générer un start
		Dependencies_start_TS = [activity[1]['start_TS'] 
			for activity in HAS['Activities'].items()
			if activity[0] in schedule_value
		]
		if schedule_nature in ['before_any', 'with_any']:
			HAS['Activities'][node_ID[0]].update({node_ID[1] + "_TS": #L'aiguillage se fait par node_ID[1] car seul un node start peut avoir un before et seul un node end peut avoir un with
				min(Dependencies_start_TS)
			})
		elif schedule_nature in ['before_all', 'with_all']:
			HAS['Activities'][node_ID[0]].update({node_ID[1] + "_TS": 
				max(Dependencies_start_TS)
			})

	elif schedule_nature in ['after_any', 'after_all']: #Les nodes start et end peuvent tous deux avoir un after, là encore on aiguille par node_ID[1] pour savoir le champs de activity à MaJ
		Dependencies_end_TS = [activity[1]['end_TS']
			for activity in HAS['Activities'].items()
			if activity[0] in schedule_value
		]
		if schedule_nature == 'after_any':
			HAS['Activities'][node_ID[0]].update({node_ID[1] + "_TS": 
				min(Dependencies_end_TS)
			})
		elif schedule_nature == 'after_all':
			HAS['Activities'][node_ID[0]].update({node_ID[1] + "_TS": 
				max(Dependencies_end_TS)
			})

	#	QUANTITY (duration)
	elif schedule_nature in ['cargo_%', 'cargo_tons']:
		if schedule_nature == "cargo_%":
			amount = HAS['handling_description']["content_amount"] * schedule_value / 100
		elif schedule_nature == "cargo_tons":
			amount = schedule_value					
		operation_throughput = get_operation_throughput(operation_description.get("work"), HAS['Machines_descriptions']) 
		if operation_throughput[0] :
			HAS['Activities'][node_ID[0]].update({"duration": 
				datetime.timedelta(minutes= (amount / operation_throughput[1]) * 60)
			})
			HAS['Activities'][node_ID[0]].update({"end_TS": 
				HAS['Activities'][node_ID[0]]["start_TS"] + HAS['Activities'][node_ID[0]]["duration"]
			})
		else :
			HAS["Logs"].append(f"Issue for handling {HAS['handling_description']['handling_ID']}, in SC {HAS['handling_description']['Supplychains'][0]} for operation {node_ID}. Issue: {operation_throughput[1]} Handling discarted")

	#TODO Rajouter un test de cohérence (start + duration = end et duration >0 )

	return #HAS

def get_operation_throughput(work:dict, Machines:list)-> tuple: 
	'''From: operation's work, port's machine collection
	Give: 
	==> (success, operation's throughput, error message)
	'''
	#TODO permettre différents throughput par content-type dans le DM des ressources ? Si oui ajouter handling_content_type en input
	success = False
	data = ["Inconsistent operation:"] #FIXME devrait être un dict
	Throuputs = []

	#RETRIVE MACHINES THROUPUTS
	for machine_ID in work["machines"]:
		throuput = next(
			(machine["throughput"]
				for machine in Machines
				if machine["ID"] == machine_ID
			), None
		)
		if throuput is None:
			data.append(f'Unable to retrive {machine_ID} throughput')
		else:
			Throuputs.append(throuput)					

	#CHECK UNIT CONSISTENCY
	if len(data) == 1:
		Units = [throuput["Unit"] #Attention, le DM est inconsistant, parfois maj, parfois pas
			for throuput in Throuputs
		]
		if len(set(Units)) > 1 :
			data.append(f"All machines from an operation should have the same unit (create another parrallele operation if needed). Details : {Throuputs}")
	
	#CALCUL OPERATION THROUPUT
	if len(data) == 1: #FIXME hack à mettre au propre : s'il y a eut une erreur (détéctée), on a append un message dans l'array qui à une len >1
		Values = [throuput["Value"]
			for throuput in Throuputs
		]
		if work["nature"] == "parallel":
			data = sum(Values)
		if work["nature"] == "series": #FIXME vérifier si c'est bien ce mot clé dans le DM Supplychains utilisé par ProD
			data = min(Values)

		if isinstance(data, int):
			if data > 0 :
				success = True
			else:
				data.append(f"The operation throuput would be {data}, which is no suitable for an duration with a nature 'cargo amount'.")

	return (success, data)

def get_next_resource_availability(resource_ID: str, resources_register: dict)-> str:
 pass #FIXME