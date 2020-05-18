# from datetime import datetime 
# from datetime import timedelta
import datetime #Contrainte pr les tests de type

def process(HANDLINGS, PORT, LOGS, SETTINGS, module_name) :
	'''
	For each handling, assign a list of activities (practical handling processing unit). That is to say SC's operations (theoritical processing unit) completed with {start TS, duration, end TS). NB: if the concurency management is activated, the handlings prioritition module should executed before in the pipeline.
	'''
	#FIXME devrait être précéder du module de prioritisation
	#FIXME concurence for ressource use should be an activable option in settings

	#INITIALIZATION
	LOGS.append(f"<==== {module_name} STARTS ====>")
	#listes pr conditionnalitées
	Nature_dependencies = [ "before_any", "before_all","with_any", "with_all", "after_any", "after_all"] #Liste de références
	Nature_quantities = ["cargo_tons", "cargo_%"] #Liste de références
	Invalide_duration_quantities = [] #Pr les logs
	Invalide_dependancies = [] #Pr les logs
	Machines_register = {} #Stocke les temps d'utilisation des machines
	

	#PROCESSING	
	for handling in HANDLINGS:
		#NEW HANDLING INITIALIZATION 
		Operations = next(
			(port_sc["steps_list"] #Retrieving SC's operation description
			for port_sc in PORT["Supplychains"] #Unretrievable handling's SC already filtered in SC assignation modul
			if port_sc["ID"] == handling["Supplychains"][0]), #Only the operations of the first suitable handling's SC is considered
			None 
		)
		for operation in Operations:  #Inside buffer, item are in a transitory state between operation and activity
			operation["start_TS"] = None #Seeding
			operation["duration"] = None
			operation["end_TS"] = None
		
		Buffer_current = deepcopy(Operations) #Operation that are adressed in this run
		Buffer_next = [] #Operation that will be adressed again next run
		Activities = [] #Operation succeffuly converted to activities

		#SCHEDULING
		#	CHECK FOR CIRCULAR DEPENDENCIES
		success, data = circular_dependencies(Operations) #Devrait être testé à la création de la SC

		#	REQUEST TS
		for operation in Buffer_current:
			success, data = get_request_TS(operation, Buffer_current + Buffer_next + Activities)

		#	CONVERT TS #On sépare la validation de dispo de machine car la séquence de priorité d'attribution n'est pas la séquence de résolution des TS_request des opérations
		#		SORT OPERATION #L'operation qui a le start_TS min dans la chaine de dépendence qui a l'opération dont le end_TS max
		Queue_operations = []
		for operation in Queue_operations:
			scheduling = correcting_TS_for_machine_availability(operation, Machines_register)
			if scheduling[0]:
				operation = scheduling[1]
				Machines_register = update_Machines_register(operation, Machines_register) #Incorporer cette étape dans correcting_TS_for_machine_availability?


			
			#MAJ du Machines_register
			# if start et end is not None:
			# 	ajouter l'occupation des machines concernées ds le registre

			# Nettoyage activity
	#CLOTURE
	#on clean les champs à surpimer (scheduling etc)	
	#on alimente les logs
	LOGS.append(f"====> {module_name} ENDS <====")
	return HANDLINGS, PORT, LOGS, SETTINGS

#=====================================================
def circular_dependencies(Operations): 
	'''
	FROM: 
		list of all operations' descriptions for the current handling's SC
	GIVE:
		(status=error, error message)
		(status=True, list of operations included in a circular reference)
		(success=False, None)
	'''	
	status = 'error'
	data = None

	#FIXME

	status = False
	data = None
	return success, data

def get_request_TS(operation, knowlege):
	'''
	FROM: 
		targeted operation's description,
		all current handling's operations (been resolved or not)
	GIVE:
		(status=error, error message)
		(status=resolved, operation with complet candidat scheduling information)
		(status=unresolved, operation with uncomplet candidat scheduling information)
	'''
	status = 'error'
	data = None
	
	#DURATION
	if operation["duration"] == None:
		nature = operation["scheduling"]["duration"].get("nature")
		value = operation["scheduling"]["duration"].get("value")
		#DELAY
		if nature == "delay":
			operation["duration"] = datetime.timedelta(minutes= value)
		#QUANTITY
		if nature in Nature_quantities:
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
			# retrieveDependancy_status, retrieveDependancy_data = retrieve_dependency(nature, value, Buffer_current + Activities) 
			
	#START
	if operation["start_TS"] == None:
		nature = operation["scheduling"]["start"].get("nature")
		value = operation["scheduling"]["start"].get("value")
		#DELAY
		if nature == "delay":
			operation['start_TS_request'] = handling['handling_earliestStart'] + datetime.timedelta(minutes= value)
		#DEPENDANCY
		if nature in Nature_dependencies:
			retrieveDependancy_status, retrieveDependancy_data = retrieve_dependency(nature, value, Buffer_current + Activities)
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
		#START_REQUEST CONVERSION
		if operation.get('start_TS_request') is not None:
			success, data = convert_startRequest(
				operation['start_TS_request'], 
				operation['duration'],
				operation['work']["machines"],
				Machines_register
			)
			if success :
				operation['start_TS'] = data
	#END
	if operation["end_TS"] == None and operation["start_TS"] != None and operation["duration"] != None:
		operation["end_TS"] = operation["start_TS"] + datetime.timedelta(minutes= operation["duration"])
	
	return (status, data)

def get_operation_throughput(work, Machines)-> (tuple): 
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
			data.append(f"All machines from an operation should have the same unit (creat another parrallele operation if needed). Details : {Throuputs}")
	
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

def retrieve_dependency(scope:str, Targets:list, Knowledge:list)-> tuple:
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

def convert_startRequest(candidat_TS, candidat_duration, Machine_IDs, Machines_register):#FIXME
	success = False
	data = None

	# for machine_ID in Machine_IDs:
	# 	#Isolation de la time line de la machine
	# 	timeline = Machines_register.get("machine_ID", [])
		
	# 	#Merge des timeline
	success = True
	data = candidat_TS

	return success, data

def correcting_TS_for_machine_availability(operation):
	'''Considering operation_request_TS and Machines_register, find the next suitable timeslot (start & end)
	'''
	success = 
	return (success, operation)