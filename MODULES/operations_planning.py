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
	LOGS.append(f"==== {module_name}  ====")
	Invalide_handlings = [] #Pr les logs
	Errors_details = [] #Pr les logs
	Errors_synthesise = {} #Pr les logs

							
	#PROCESSING	
	for handling in HANDLINGS:
		#OPERATIONS RESOLUTION
		HAS = create_HAS(handling, PORT["supplychains"], PORT["resources"])
		for node_ID in HAS["graph"]:
			if node_ID in HAS["unchecked"]:
				HAS["stack"] = []
				wander_HAS(node_ID, HAS)#Obligé de tout mettre dans cette fonction pr la récursivité
			if HAS["loop_detected"]:
				break 
		
		#IMPUTING
		handling["Activities"] = list(HAS["Activities"].values()) #On fait l'affectation avant le controle d'intégrité pr avoir le détail de l'activités calculée dans les logs pr les handlings rejetés (car incohérents)
		
		#INTEGRITY CHECK
		if HAS["error"] is not None:
			Invalide_handlings.append(handling)
			Errors_details.append(HAS["error"])

	
	#CLEANING
	for handling in Invalide_handlings:
		HANDLINGS.remove(handling)
	
	
	#LOGS
	for error in Errors_details:
		Errors_synthesise.setdefault(error['type'], {})
		Errors_synthesise[error['type']].setdefault(error["SC"], {})
		Errors_synthesise[error['type']][error["SC"]].setdefault(error["operation"], {
			"number of occurences": 0, 
			"message": error["message"],
			"handlings (see details in Activities)": []
		})
		Errors_synthesise[error['type']][error["SC"]][error["operation"]]["handlings (see details in Activities)"].append(error["handling"])
		Errors_synthesise[error['type']][error["SC"]][error["operation"]]["number of occurences"] = len(Errors_synthesise[error['type']][error["SC"]][error["operation"]]["handlings (see details in Activities)"])


	#---------------------------------------------------
	#DEBUG: EXPORT HANDLINGS FOIREUX #FIXME supprimer
	# import json
	# import statistics 
	# export = {
	# 	"handlings_OK": HANDLINGS,
	# 	"handlings_HS": Errors_synthesise
	# }
	# with open("./error_OpPlan.json", 'w') as file:
	# 	json.dump(export, file, indent=4, default=str)

	# hand_OK = HANDLINGS
	# amount_OK = [handling['content_amount'] for handling in hand_OK]
	# print("\nOK")
	# print(min(amount_OK))
	# print(max(amount_OK))
	# print(statistics.mean(amount_OK))
	# print(statistics.median(amount_OK))

	# hand_HS = Invalide_handlings
	# amount_HS = [handling['content_amount'] for handling in hand_HS]
	# print("\nHS")
	# print(min(amount_HS))
	# print(max(amount_HS))
	# print(statistics.mean(amount_HS))
	# print(statistics.median(amount_HS))

	#---------------------------------------------------

	LOGS.append(f"Number of handlings for which activities could not be established and been discarted: {len(Invalide_handlings)}") 
	if len(Invalide_handlings) > 0:
		LOGS.append({"Details": Errors_synthesise})
	return HANDLINGS, PORT, LOGS

#=====================================================
def create_HAS(handling:dict, SUPPLYCHAINS: dict, RESOURCES: dict)-> dict:
	'''Prepare material for operations batch resolution:
	- convert the list of operation to a graph of node (each operation O been split in 2 nodes: 0_start & O_end)
	- initialize some list and variables
	'''
	#TODO les graphes ne devraient pas être recalculés individuellement et à chaque fois ! Tout ce bloc doit être placé en amont (idéalement à la création d'une SC, c'est tout le prb)
	#TODO refaire en faisant une classe. Au lieu d'utiliser des listes, donner un status aux noeuds du graphe
	#TODO a minima, reprendre le formalisme précédent (encapsuler dans un try, sortir le tuple (success/status, data/error))

	#RETRIVE DATA
	Operations = SUPPLYCHAINS[handling['assigned_SC_ID']]['operations']
	Resources = RESOURCES
	# variante légacy{ID: RESOURCES[ID] 
	# 	for ID in [resource_ID for operation in Operations for resource_ID in operation['ressources_uses']['ressources_IDs']]
	# }
	
	#BUILD GRAPH
	SC_graph = {} 
	for ope_ID, ope_content in Operations.items():
		#START NODE DEPENDENCIES
		schedule_nature = ope_content['scheduling']['start']['nature']
		schedule_value = ope_content['scheduling']['start']['value']
		SC_graph[(ope_ID, "start")] = [] #Valeur par défaut
		if schedule_nature in ["with_any", "with_all"]:
			SC_graph[(ope_ID, "start")] = list(set([(parent, "start") for parent in schedule_value]))
		if schedule_nature in ["after_any", "after_all"]:
			SC_graph[(ope_ID, "start")] = list(set([(parent, "end") for parent in schedule_value]))
			
		#END NODE DEPENDENCIES
		schedule_nature = ope_content['scheduling']['duration']['nature']
		schedule_value = ope_content['scheduling']['duration']['value']
		default = [(ope_ID, "start")] #Valeur par défaut: Toute fin d'opération dépend du début de l'opération (même si le début n'a pas de dépendence, afin de garantir qu'on parcours le graphe entier, condition pour que toutes les opérations soient résolues)
		SC_graph[(ope_ID, "end")] = default
		if schedule_nature not in ["delay", "duration"]:
			if schedule_nature in ["before_any", "before_all"]:
				cible = "start"
			if schedule_nature in ["after_any", "after_all"]:
				cible = "end"
			SC_graph[(ope_ID, "end")] = list(set(default + [(parent, cible) for parent in schedule_value])) #NB bien inclure le default avant d'appliquer le set()

	#MERGE ALL INTO A HANDLING ACTIVITIES SCENARIO
	HAS = { #NB On pourrait remplacer par une classe
		#CONTEXTE
		"Operations_descriptions": Operations,
		"Resources": Resources,
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
			HAS["error"] = { #TODO refactoroser
				"type": "infinit loop",
				"SC": next(iter(HAS['handling_description']["Supplychains_IDs"])),
				"operation": node_ID[0],
				"handling": {HAS['handling_description']["handling_ID"]: HAS['handling_description']},
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
	operation = HAS['Operations_descriptions'].get(node_ID[0]) #TODO mettre un get ?
	# variante legacy next((operation
	# 	for operation in HAS['Operations_descriptions']
	# 	if ope_ID == node_ID[0]),
	# 	None
	# )

	#	INSTANTIATE ACTIVITY IN HAS 
	if node_ID[0] not in HAS['Activities']:
		HAS['Activities'][node_ID[0]] = { #Attention, ici on sort de la structure "usuelle", pas de champs ID mais mais un nom de dict
			"operation_ID": node_ID[0],
			"Resources_IDs": operation['ressources_uses']['ressources_IDs'] #On ne l'utilise pas ici, mais plus simple de générer ici pour les modules en aval.
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
		success, operation_throughput = get_operation_throughput(operation.get('ressources_uses'), HAS['Resources'])
		if success :
			activity.update({"duration": 
				datetime.timedelta(minutes= (amount / operation_throughput) * 60)
			})
			activity.update({"end_TS": 
				activity["start_TS"] + activity["duration"]
			})
		else:
			pass #FIXME on a un plantage en aval si on obtient pas de end_TS ici !  TODO ajouter log operation_throughput contient toutes les infos d'erreur
	
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
				min(Dependencies_end_TS) #FIXME ajouter si val < start, alors prendre start (pr durée à 0 et non négative ?)
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
		success = activity_consistency_test(activity) #TODO si n opérations pausent problème, toutes devraient être remontées ds data, pas uniquement la première
		if not success:
			HAS["error"] = {#TODO refactoroser
				"type": "inconsistent TimeStamp",
				"SC": next(iter(HAS['handling_description']["Supplychains_IDs"])),
				"operation": node_ID[0],
				"handling": {HAS['handling_description']["handling_ID"]: HAS['handling_description']},
				"message": f"Issue for operation {node_ID[0]}. Resulting activity timestamp inconsistent."
			}

	
		
		
		#Convertir ici la durée en nb d'heures (float) duration.total_seconds() / 60 ?
	return #HAS

def get_operation_throughput(work:dict, Resources:dict)-> tuple: 
	'''From: operation's work, port's resource collection
	Give: (success, operation's throughput OR error message)
	'''
	#TODO permettre différents throughput par content-type dans le DM des ressources ? Si oui ajouter handling_content_type en input
	success = None
	data = [] #FIXME devrait être un dict

	try:
		#RETRIVE MACHINES THROUPUTS
		Throughputs = [] #[Resources[ID]["throughput"] for ID in work['ressources_IDs']] #ne permet pas de log le détail en cas d'erreur comme la version précédente
		for ID in work['ressources_IDs']:
			throughput = Resources.get(ID, {}).get("throughput")
			if throughput is None:
				success = False
				data.append(f'Unable to retrive {ID} throughput')
			else:
				Throughputs.append(throughput)					

			#CHECK UNIT CONSISTENCY
			if len(set([throughput["Unit"] for throughput in Throughputs])) > 1 : #Attention, le DM est inconsistant, parfois maj, parfois pas
				success = False
				data.append(f"In one operation, all machines should have the same  throughput unit (create another dependent operation if needed). Details : {Throughputs}")

			#CALCUL OPERATION THROUPUT
			else:
				Values = [throughput["Value"] for throughput in Throughputs]
				if work["nature"] == "parallel":
					operation_throughput = sum(Values)
				if work["nature"] == "sequential": #NB attention, dans certains DM c'est serial
					operation_throughput = min(Values)

				if isinstance(operation_throughput, int):
					if operation_throughput > 0 :
						success = True
						data = operation_throughput
					else:
						success = False
						data.append(f"The operation throuput would be {data}, which is no suitable for an duration with a nature 'cargo amount'.")

	except Exception as error:
		success = False
		data.append(f'Error during operation throughput calculation. Detail: {error}')

	return success, data


def get_next_resource_availability(resource_ID: str, resources_register: dict)-> str:
 pass #FIXME

def activity_consistency_test(activity: dict)-> tuple:
	success = False
	#data = None

	Inconsistency_conditions = [
		(None in [activity["start_TS"], activity["end_TS"], activity["duration"]]),
		(activity["start_TS"] > activity["end_TS"]),
		(activity["duration"] != activity["end_TS"] - activity["start_TS"])
	]
	if True in Inconsistency_conditions:
		success = False
	else:
		success = True
	
	return success#, data