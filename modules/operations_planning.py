# from datetime import datetime 
# from datetime import timedelta
import datetime #Contrainte pr les tests de type


def main(HANDLINGS, PORT, LOGS, SETTINGS, module_name) :
	'''
	For each handling, assign a list of activities (practical handling processing unit). That is to say SC's operations (theoritical processing unit) completed with {start TS, duration, end TS). NB: if the concurency management is activated, the handlings prioritition module should executed before in the pipeline.
	'''
	#FIXME devrait être précéder du module de prioritisation
	#FIXME concurence for ressource use should be an activable option in settings
	#NB: un premier bloc de fonction (qui pourrait être des méthodes de classe) sont définies en entete de main pour ne pas avoir à faire des appels très lourds. Ce sont des fonctions qui ne renvoient rien mais modifient des objects dans le scope courant (cad un handling donné).
	#Les fonctions qui sont définies en dehors du main quant à elles renvoient un objet 
	'''
	Résolution:
		creat graphe
		parcours du graphe (récursif)
		resolve node candidat TS 
		corige candidat TS for machine availability
	'''
	#INITIALIZATION
	LOGS.append(f"<==== {module_name} STARTS ====>")
	#	SOME LIST	
	Invalide_handlings = [] #Pr les logs
	Errors_details = [] #Pr les logs
	Errors_synthesise = {} #Pr les logs

	#	==> DEBUG
	#Check doublons input
	len([handling['handling_ID'] for handling in HANDLINGS]) == len(set([handling['handling_ID'] for handling in HANDLINGS]))
	
	nb_hand_initial = len(HANDLINGS)
	print(f"nb_hand_initial: {nb_hand_initial}")
	counter_handling_processed =0
		
	#PROCESSING	
	for handling in HANDLINGS:
		#OPERATIONS RESOLUTION
		HAS = create_HAS(handling, PORT["Supplychains"], PORT["Resources"]["machines"])
		for node_ID in HAS["graph"]:
			if node_ID in HAS["unchecked"]:
				HAS["stack"] = []
				wander_HAS(node_ID, HAS)#Obligé de tout mettre dans cette fonction pr la récursivité
			if HAS["loop_detected"]:
				break 
		
		handling["Activities"] = list(HAS["Activities"].values()) #On fait l'affectation avant le controle d'intégrité pr avoir le détail de l'activités calculée dans les logs pr les handlings rejetés (car incohérents)
		
		#INTEGRITY CHECK
		if HAS["error"] is not None:
			Invalide_handlings.append(handling)
			Errors_details.append(HAS["error"])
			counter_handling_processed +=1
			print(HAS["error"])
		
		# if "Activities" not in handling.keys():
		# 	Invalide_handlings.append(handling)
		# 	Errors_details.append({
		# 		"type": "no activities inputed",
		# 		"SC": next(iter(HAS['handling_description']["Supplychains_IDs"])),
		# 		"operation": 'undetermined',
		# 		"message": f"For unknow raison, no activities where imputed to this handling"
		# 	})
		
	print(f"counter_handling_processed: {counter_handling_processed}")
	# # <<ajouter les handling sans Activities ?
	ss_activities = [handling for handling in HANDLINGS if "Activities" not in handling.keys()]
	# for handling in ss_activities:
	# 	HANDLINGS.remove(handling)
	#CLOTURE
	for error in Errors_details:
		Errors_synthesise.setdefault(error['type'], {})
		Errors_synthesise[error['type']].setdefault(error["SC"], {})
		Errors_synthesise[error['type']][error["SC"]].setdefault(error["operation"], {
			"number of occurences": 0,
			"detail": error["message"]
		})
		Errors_synthesise[error['type']][error["SC"]][error["operation"]]["number of occurences"] += 1

	#---------------------------------------------------
	#DEBUG HANDLINGS FOIREUX
	print(f"nb_hand_final: {len(HANDLINGS)}")
	#	PRINT
	ID_ss_activities = 	[handling['handling_ID'] for handling in ss_activities]
	ID_invalides = 		[handling['handling_ID'] for handling in Invalide_handlings]
	ID_oks = 			[handling['handling_ID'] for handling in HANDLINGS]

	print(f"============================\nnb de handling :")
	print(f"intial: 			{nb_hand_initial}")
	print(f"sans Activities: 	{len(ss_activities)}")#, 		{ID_ss_activities}")
	print(f"incohérents: 		{len(ID_invalides)}")#,  	{ID_invalides}")
	print(f"ok ?: 				{len(ID_oks)}")#, 			{ID_oks}")
	
	count_invalides_U_ssActivities = 0
	for handling_ID in ID_ss_activities:
		if handling_ID in ID_oks:
			count_invalides_U_ssActivities += 1
			# print(handling_ID)
	print(count_invalides_U_ssActivities)
	#	DEBUG EXPORT
	import json
	export = {
		"invalid handlings (loop et duration)": Invalide_handlings,
		"ss activities": ss_activities
	}
	with open("./handlings_activities_HS.json", 'w') as file:
		json.dump(export, file, indent=4, default=str)
	#---------------------------------------------------

	LOGS.append(f"Number of handlings for which activities could not be established and been discarted: {len(Invalide_handlings)}") 
	if len(Invalide_handlings) > 0:
		LOGS.append({"Details": Errors_synthesise})
		LOGS.append({"Discarted handlings": Invalide_handlings}) #TODO ne pas mettre tous les handlings ici, mais les ventiler par cause de rejet (dc dans Errors_synthesise)
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
			if port_sc["ID"] == handling["Supplychains_IDs"][0]), #Only the operations of the first suitable handling's SC is considered
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
		#RESULTS
		"Activities":{},
		"error": None
	} 
	
	return HAS

def wander_HAS(node_ID:tuple, HAS: dict)-> None:
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
			HAS["error"] = {
				"type": "infinit loop",
				"SC": next(iter(HAS['handling_description']["Supplychains_IDs"])),
				"operation": node_ID[0],
				"message": f"Issue for operation {node_ID[0]} (boundarie {node_ID[1]} call for the parent operation {parent_ID}, creating an infinit loop."
			}
				
			break
		if parent_ID in HAS["unchecked"]:# Appel récursif sur les dépendences de l'opération
			wander_HAS(parent_ID, HAS)
	
	#RESOLUTION DU NOEUD
	if not HAS["loop_detected"]:
		HAS["unchecked"].remove(node_ID)
		HAS["checked"].append(node_ID) #Le noeud à toutes ces dépendances résolues (y comprit node_start pour un node_end)
		resolve_node(node_ID, HAS) #Le start d'une opération passe forcement en premier, puis le end. On a alors l'entièreté de l'opération qui devient par définition une activitéactivité)

	return #HAS

def resolve_node(node_ID:tuple, HAS: dict)-> None: #Cette fonction n'est qu'une isolation formelle du bloc de code
	#INITIALIZATION

	#	RETRIVE OPERATION DESCRIPTION FROM PORT
	operation = next((operation
		for operation in HAS['Operations_descriptions']
		if operation["ID"] == node_ID[0]),
		None
	)

	#	INSTANTIATE ACTIVITY IN HAS 
	if node_ID[0] not in HAS['Activities']:
		HAS['Activities'][node_ID[0]] = { #Attention, ici on sort de la structure "usuelle", pas de champs ID mais mais un nom de dict
			"operation_ID": node_ID[0],
			"Resources_IDs": operation['work']['machines'] #On ne l'utilise pas ici, mais plus simple de générer ici pour les modules en aval.
		} 

	#	SHORTCUT
	activity = HAS['Activities'][node_ID[0]] #Simple shortcut
	
	if node_ID[1] == "start":
		key = "start"
	elif node_ID[1] == "end":
		key = "duration" #Dans le DM, l'info pour end est fusionnée avec duration
	schedule_nature = operation["scheduling"][key].get("nature")
	schedule_value = operation["scheduling"][key].get("value")

	
	# ACTIVITY RESOLUTION #On pourrait séparer en sub fonction distinctes, mais à quoi bon ? #NB: on parcours simplement l'arborescence des possibles avec les elif
	
	#	DELAY (start ou duration)
	if schedule_nature == "delay": 
		if node_ID[1] == "start":#TODO DM maj; plus de delais pr start
			activity.update({"start_TS":
				HAS['handling_description']['handling_earliestStart'] + datetime.timedelta(minutes= schedule_value) #NB Attention à l'unité saisie par l'utilisateur
			})
		elif node_ID[1] == "end":
			activity.update({"duration": 
				datetime.timedelta(minutes= schedule_value)
			})

	#	QUANTITY (duration)
	elif schedule_nature in ['cargo_%', 'cargo_tons']:
		if schedule_nature == "cargo_%":
			amount = HAS['handling_description']["content_amount"] * schedule_value / 100
		elif schedule_nature == "cargo_tons":
			amount = schedule_value					
		operation_throughput = get_operation_throughput(operation.get("work"), HAS['Machines_descriptions']) 
		if operation_throughput[0] :
			activity.update({"duration": 
				datetime.timedelta(minutes= (amount / operation_throughput[1]) * 60)
			})
			activity.update({"end_TS": 
				activity["start_TS"] + activity["duration"]
			})
	
	#	DEPENDENCY (start ou end)
	#		ACTIVITY START
	elif schedule_nature in ["before_any", "before_all","with_any", "with_all"]: #Tous pointent vers un start d'opération, mais les before pour générer un end tandis que les with pr générer un start
		Dependencies_start_TS = [parent_activity[1]['start_TS'] 
			for parent_activity in HAS['Activities'].items()
			if parent_activity[0] in schedule_value
		]
		if schedule_nature in ['before_any', 'with_any']:
			activity.update({node_ID[1] + "_TS": #L'aiguillage se fait par node_ID[1] car seul un node start peut avoir un before et seul un node end peut avoir un with
				min(Dependencies_start_TS)
			})
		elif schedule_nature in ['before_all', 'with_all']:
			activity.update({node_ID[1] + "_TS": 
				max(Dependencies_start_TS)
			})

	#		ACTIVITY END
	elif schedule_nature in ['after_any', 'after_all']: #Les nodes start et end peuvent tous deux avoir un after, là encore on aiguille par node_ID[1] pour savoir le champs de activity à MaJ
		Dependencies_end_TS = [parent_activity[1]['end_TS']
			for parent_activity in HAS['Activities'].items()
			if parent_activity[0] in schedule_value
		]
		if schedule_nature == 'after_any':
			activity.update({node_ID[1] + "_TS": 
				min(Dependencies_end_TS)
			})
		elif schedule_nature == 'after_all':
			activity.update({node_ID[1] + "_TS": 
				max(Dependencies_end_TS)
			})

	#		ACTIVITY DURATION
	if node_ID[1] == "end": #D'après la condition de dépendence, alors ce node n'est résolu que si son start est résolu
		activity.update({"duration": #NB un peu hacky de recalculer les durations pr TOUS les cas
			activity["end_TS"] - activity["start_TS"]
		})
	
	#	CLOSING
		success, data = activity_consistency_test(activity)
		if not success:
			HAS["error"] = {
				"type": "inconsistent TimeStamp",
				"SC": next(iter(HAS['handling_description']["Supplychains_IDs"])),
				"operation": node_ID[0],
				"message": f"Issue for operation {node_ID[0]}. Resulting activity timestamp inconsistent."
			}

	
		
		
		#Convertir ici la durée en nb d'heures (float) duration.total_seconds() / 60 ?
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

def activity_consistency_test(activity: dict)-> tuple:
	success = False
	data = None

	Inconsistency_conditions = [
		(None in [activity["start_TS"], activity["end_TS"], activity["duration"]]),
		(activity["start_TS"] > activity["end_TS"]),
		(activity["duration"] != activity["end_TS"] - activity["start_TS"])
	]
	if True in Inconsistency_conditions:
		success = False
	else:
		success = True
	
	return success, data