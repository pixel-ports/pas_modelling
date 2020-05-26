# from datetime import datetime 
# from datetime import timedelta
import datetime #Contrainte pr les tests de type
import re #A supprimer lors de la refonte au prorpre


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
		parcours du graphe
			resolve duration
				delais
				amount
					resolve throuhput
				dependencies
			resolve start
				delais (c'est une dépendence à op_0 + un deltatime)
				dependencies
	'''
	#INITIALIZATION
	LOGS.append(f"<==== {module_name} STARTS ====>")
	#	SOME LIST
	Nature_dependencies = [ "before_any", "before_all","with_any", "with_all", "after_any", "after_all"] #Liste de références
	
	Invalide_duration_quantities = [] #Pr les logs
	Invalide_dependancies = [] #Pr les logs
	

	def run_process_graph(node_ID:str, process:dict)->None:
		'''Recursive function that go accross all the operations graph to:
		- check if there is a dependency loop
		- call for operation resolution (get TS) when it's dependencies are resolved.
		NB: there is no return, modifications are affected directly to objects
		'''

		def resolve_node_start(node_ID: str)-> None:
			'''
			'''
			nonlocal operation
			#START
			if operation["start_TS"] == None:
				nature = operation["scheduling"]["start"].get("nature")
				value = operation["scheduling"]["start"].get("value")
				#DELAY
				if nature == "delay":
					operation['start_TS_request'] = handling['handling_earliestStart'] + datetime.timedelta(minutes= value)
				#DEPENDANCY
				if nature in Nature_dependencies:
					retrieveDependancy_status, retrieveDependancy_data = get_dependency_TS(nature, value, Buffer_current + Activities)
					#TODO modifier en else pr ne pas laisser des trous dans la raquette ?
					if retrieveDependancy_status == "success":
						operation["start_TS"] = retrieveDependancy_data
					elif retrieveDependancy_status == "undetermined":
						Buffer_next.append(operation)
					elif retrieveDependancy_status == "invalide_dependency": 
						Invalide_dependancies.append({
							"children operation": operation,
							"parent operation (unresolved)": operation,
							"supplychain name": handling["Supplychains"][0], 
							"handling": handling, #Remplacer pr le nombre d'handlings concernés
						}) #FIXME mettre au propre ce dict de log

		def resolve_node_end(node_ID: str)-> None:
			'''Since an end note would be resolve only after the corresponding start node is resolved, here both duration and end are resolved
			'''
			#DURATION
			if operation["duration"] == None:
				nature = operation["scheduling"]["duration"].get("nature")
				value = operation["scheduling"]["duration"].get("value")
				#DELAY
				if nature == "delay":
					operation["duration"] = datetime.timedelta(minutes= value)
				#QUANTITY
				if nature in ["cargo_tons", "cargo_%"]:#Lors de la MaJ, passer par liste de références
					if nature == "cargo_%":
						amount = handling["content_amount"] * value / 100
					if nature == "cargo_tons":
						amount = value					
					operation_throughput = get_operation_throughput(operation.get("work"), PORT["Resources"]["machines"]) 
					if operation_throughput[0] :
						operation["duration"] = datetime.timedelta(minutes= (amount / operation_throughput[1]) * 60)
						
					else :
						Invalide_duration_quantities.append({"operation": operation, "issue": operation_throughput[1]})#FIXME on ne passe pas la liste à la fonction
				#DEPENDANCY
				if nature in Nature_dependencies:
					pass
					# retrieveDependancy_status, retrieveDependancy_data = retrieve_dependency(nature, value, Buffer_current + Activities)
			#END
			if operation["end_TS"] == None and operation["start_TS"] != None and operation["duration"] != None:
				operation["end_TS"] = operation["start_TS"] + datetime.timedelta(minutes= operation["duration"]) 

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

		def get_dependency_TS(scope:str, Targets:list, Knowledge:list)-> tuple:
			'''
			Try to retrieve current operation end_TS from targeted operations start and end TS. 
			'''
			#NB attention, ici une petite erreur d'inatention sur la logic peut compromettre la logic tout en sortant des résultats formellement valides
			success = False
			data = None

			#TARGETS START ==> BEFORE (duration) & WITH (start)
			if scope in ['before_any', 'with_any', 'before_all', 'with_all']:#On ne génère la liste que que si elle est utilisée
				try: 
					Start_TSs = [operation['start_TS'] 
						for operation in Knowledge
						if operation["ID"] in Targets
					]
					if scope in ['before_any', 'with_any'] :
						data = min(Start_TSs)
					if scope in ['before_all', 'with_all'] :
						data = max(Start_TSs)
				except Exception as error:
					data = error
			
			#TARGETS END ==> AFTER
			if scope in ['after_any', 'after_all']:
				try:
					End_TSs = [operation['end_TS']
						for operation in Knowledge
						if operation["ID"] in Targets
					]
					if scope == 'after_any':
						data = min(End_TSs)
					if scope == 'after_all':
						data = max(End_TSs)
				except Exception as error:
					data = error

			if isinstance(data, datetime.datetime):
				success = True

			return success, data

		#FONCTION RECURSSIVE DE PARCOURS DE GRAPHE (AVEC RÉSOLUTION)
		process["stack"].append(node_ID)
		# global loop_detected
		if process["loop_detected"]:
			return
		
		for parent_ID in process["graph"][node_ID]:
			# Détection d'une boucle dans le graphe
			if parent_ID in process["stack"]:
				process["loop_detected"] = True 
				return
			# Appel récursif sur les dépendences de l'opération
			if parent_ID in process["unchecked"]:
				run_process_graph(parent_ID, process)
		#EN L'ABSCENCE DE DÉPENDANCE, RÉSOLUTION DE L'OPERATION
		
		operation = [operation_description
			for operation_description in process["description"]["steps_list"]
			if operation_description["ID"] == node_ID[0]
		]
		assert len(operation) ==1, "multiples opération descriptions renvoyées"#FIXME
		#FIXME attention, ici ne pas inclure la dépendence au début de l'opération
		process["checked"].append(node_ID)
		return

	#PROCESSING	
	for handling in HANDLINGS:

		#OPERATIONS RESOLUTION
		process = create_process(handling["Supplychains"][0], PORT["Supplychains"], PORT["Resources"]["machines"])

		for node_ID in process["graph"]:
			if node_ID in process["unchecked"]:
				process["stack"] = []
				run_process_graph(node_ID, process)
			if process["loop_detected"]:
				break

		#	AFFICHAGE RESULTAT
		if process["loop_detected"]:
			print("PRB, boucle détectée !")
		elif process["loop_detected"] == False:
			print("Ok, pas de boucle détectée")
		else:
			print("Autre cas. Etrange")

			# Nettoyage activity
	#CLOTURE
	#on clean les champs à surpimer (scheduling etc)	
	#on alimente les logs
	LOGS.append(f"====> {module_name} ENDS <====")
	return HANDLINGS, PORT, LOGS, SETTINGS

#=====================================================
def create_process(SC_ID:str, Supplychains_collection: list, Machines_collection: list)->dict:
	'''Prepare material for operations batch resolution:
	- convert the list of operation to a graph of node (each operation O been split in 2 nodes: 0_start & O_end)
	- initialize some list and variables
	'''
	#TODO les graphes ne devraient pas être recalculés individuellement et à chaque fois ! Tout ce bloc doit être placé en amont (idéalement à la création d'une SC, c'est tout le prb)
	#TODO refaire en faisant une classe. Au lieu d'utiliser des listes, donner un status aux noeuds du graphe
	#TODO a minima, reprendre le formalisme précédent (encapsuler dans un try, sortir le tuple (success/status, data/error))

	#GET SC DATA
	SC_description = next(
			(port_sc#["steps_list"] #Retrieving SC's operation description
			for port_sc in Supplychains_collection #Unretrievable handling's SC already filtered in SC assignation modul
			if port_sc["ID"] == SC_ID), #Only the operations of the first suitable handling's SC is considered
			None 
		)

	#BUILD GRAPH
	SC_graph = {} 
	for operation in SC_description["steps_list"]:
		#START NODE DEPENDENCIES
		start_nature = operation['scheduling']['start']['nature']
		start_value =  operation['scheduling']['start']['value']
		SC_graph[(operation["ID"], "start")] = [] #Valeur par défaut
		if start_nature in ["with_any", "with_all"]:
			SC_graph[(operation["ID"], "start")] = list(set([(parent, "start") for parent in start_value]))
		if start_nature in ["after_any", "after_all"]:
			SC_graph[(operation["ID"], "start")] = list(set([(parent, "end") for parent in start_value]))
			
		#END NODE DEPENDENCIES
		end_nature = operation['scheduling']['duration']['nature']
		end_value =  operation['scheduling']['duration']['value']
		default = [(operation["ID"], "start")] #Valeur par défaut: Toute fin d'opération dépend du début de l'opération (même si le début n'a pas de dépendence, afin de garantir qu'on parcours le graphe entier, condition pour que toutes les opérations soient résolues)
		if end_nature in ["before_any", "before_all"]:
			SC_graph[(operation["ID"], "end")] = list(set(default + [(parent, "start") for parent in end_value])) #NB bien inclure le default avant d'appliquer le set()
		if end_nature in ["after_any", "after_all"]:
			SC_graph[(operation["ID"], "end")] = list(set(default + [(parent, "end") for parent in end_value]))

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

	#MERGE ALL
	process = {
		"description": SC_description,
		"graph": SC_graph,
		"unchecked":list(SC_graph.keys()),
		"stack": [],
		"checked":[],
		"loop_detected": False,
		"Machines": SC_machine_descriptions
	} 
	
	return process

