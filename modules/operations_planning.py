# from datetime import datetime 
# from datetime import timedelta
import datetime #Contrainte pr les tests de type

def process(HANDLINGS, PORT, LOGS, SETTINGS, module_name) :
	'''
	For each handling, assign a list of activities (practical handling processing unit). That is to say SC's operations (theoritical processing unit) completed with:
	- start TS, 
	- duration,
	- end TS,
	(ressources used are directly retrieved from SC's operation)

	NB:
	- concurence for ressource use should be an activable option in settings
	- if the concurency management is active, the handlings should be prioritized thought the dedicated module
	'''
	#FIXME devrait être précéder du module de prioritisation


	#INITIALIZATION
	LOGS.append(f"<==== {module_name} STARTS ====>")
	#listes pr conditionnalitées
	Nature_dependencies = [ "before_any", "before_all","with_any", "with_all", "after_any", "after_all"] #TODO garde t on le before ?
	Nature_quantities = ["cargo_tons", "cargo_%"]
	Invalide_duration_quantities = []
	Invalide_dependancies = []
	
	#PROCESSING
	'''
	Principe :
		Tant qu'on progresse dans le traitement, 
			prendre prochaine operation du Buffer_current
				déterminer pour l'operation
					duration

					start
						déterminer la primitive "au plus tot"
						récupérer la prochaine dispo machine à partir de la primitive avec une durée suffisante
					
						
					end
						calculé par start + duration
				si complette, la passer à Activities
				si incomplette, la passer à Buffer_next
			remplacer le Buffer_current par Buffer_next (et MaJ knowledge)
	'''
	for handling in HANDLINGS:
		#NEW HANDLING RESET 
		Buffer_current = next(
			(port_sc["steps_list"] #Retrieving SC's operation description
			for port_sc in PORT["Supplychains"] #Unretrievable handling's SC already filtered in SC assignation modul
			if port_sc["ID"] == handling["Supplychains"][0]), #Only the operations of the first suitable handling's SC is considered
			None 
		)
		for item in Buffer_current:  #Inside buffer, item are in a transitory state between operation and activity
			item["start_TS"] = None #Seeding
			item["duration"] = None
			item["end_TS"] = None
		
		Buffer_next = [] #Operation that will be adressed again next run
		Activities = [] #Operation succeffuly converted to activities

		#SCHEDULING
		#while len(Buffer_next) > 0 and len(Buffer_next) < len(buffer_previous):
		#while len(Activities) < len(Operations_list):
		# progression_success = True si len(Buffer_current) < len(buffer_previous) #Peut etre besoin de descendre aux 3 composants d'une activitée
		
		for item in Buffer_current:
			#DURATION
			#TODO passer la valeur en timedelta à l'enregistrement ?
			if item["duration"] == None:
				nature = item["scheduling"]["duration"].get("nature")
				value = item["scheduling"]["duration"].get("value")
				#DELAY
				if nature == "delay":
					item["duration"] = value
				#QUANTITY
				if nature in Nature_quantities:
					if nature == "cargo_%":
						operation_amount = handling["content_amount"] * value
					if nature == "cargo_tons":
						operation_amount = value					
					operation_throughput_success, operation_throughput_data = get_operation_throughput(item.get("work"), PORT["Resources"]["machines"]) #TODO modif DM: suprimer le level machines pour le passer en nature ?
					if operation_throughput_success :
						item["duration"] = operation_amount / operation_throughput_data
						
					else :
						Invalide_duration_quantities.append({"operation": item, "issue": operation_throughput_data})
				#DEPENDANCY
				if nature in Nature_dependencies:
					retrieveDependancy_status, retrieveDependancy_data = retrieve_dependency(nature, value, Buffer_current + Activities) 
			#START
			if item["start_TS"] == None:
				nature = item["scheduling"]["start"].get("nature")
				value = item["scheduling"]["start"].get("value")
				#DELAY
				if nature == "delay":
					item['start_TS_request'] = handling['handling_earliestStart'] + datetime.timedelta(minutes= value)
				#DEPENDANCY
				if nature in Nature_dependencies:
					retrieveDependancy_status, retrieveDependancy_data = retrieve_dependency(nature, value, Buffer_current + Activities)
					#TODO modifier en else pr ne pas laisser des trous dans la raquette ?
					if retrieveDependancy_status == "success":
						item["start_TS"] = retrieveDependancy_data
					elif retrieveDependancy_status == "undetermined":
						Buffer_next.append(item)
					elif retrieveDependancy_status == "invalide_dependency": 
						Invalide_dependancies.append({
							"children operation": item,
							"parent operation (unresolved)": item,
							"supplychain name": handling["Supplychains"][0], 
							"handling": handling, #Remplacer pr le nombre d'handlings concernés
						}) #FIXME mettre au propre ce dict de log
			
			#END
			if item["end_TS"] == None and item["start_TS"] != None and item["duration"] != None:
				item["end_TS"] = item["start_TS"] + datetime.timedelta(minutes= item["duration"])
			

	#CLOTURE
	#on clean les champs à surpimer (scheduling etc)	
	#on alimente les logs
	LOGS.append(f"====> {module_name} ENDS <====")
	return HANDLINGS, PORT, LOGS, SETTINGS

#=====================================================
def get_operation_throughput(Op_machines_uses, Port_machines): 
	#TODO permettre différents throughput par content-type dans le DM des ressources ? Si oui ajouter handling_content_type en input
	success = False
	data = ["Inconsistent operation:"] #FIXME devrait être un dict
	Operation_throuputs = []

	#RETRIVE MACHINES THROUPUTS
	for op_machine_ID in Op_machines_uses["machines"]:
		throuput_description = next(
			(port_machine_description["throughput"]
				for port_machine_description in Port_machines
				if port_machine_description["ID"] == op_machine_ID
			), None
		)
		if throuput_description is None:
			data.append(f'Unable to retrive {op_machine_ID} throughput')
		else:
			Operation_throuputs.append(throuput_description)
	
					

	#CHECK UNIT CONSISTENCY
	if len(data) == 1:
		Units = [throuput["Unit"]
			for throuput in Operation_throuputs
		]
		if len(set(Units)) > 1 :
			data.append(f"All machines from an operation should have the same unit (creat another parrallele operation if needed). Details : {Operation_throuputs}")
	
	#CALCUL OPERATION THROUPUT
	if len(data) == 1: #FIXME hack à mettre au propre : s'il y a eut une erreur (détéctée), on a append un message dans l'array qui à une len >1
				Units = [throuput["Unit"]
			for throuput in Operation_throuputs
		]
		if operation_work["nature"] == "parallel":
			data = sum(
				Operation_throuputs["Value"].values())
		if operation_work["nature"] == "serie": #FIXME vérifier si c'est bien ce mot clé dans le DM Supplychains
			data = min(Operation_throuputs)

		if isinstance(data, int):
			if data > 0 :
				success = True
			else:
				data.append(f"The operation throuput would be {data}, which is no suitable for an duration with a nature 'cargo amount'.")

	return success, data

def retrieve_dependency(scope:str, Targets:list, Knowledge:list)-> tuple:
	'''
	Try to retrieve current operation end_TS from targeted operations start and end TS. 
	'''
	#NB attention, ici une petite erreur d'inatention sur la logic peut compromettre la logic tout en sortant des résultats formellement valides
	success = False
	data = None

	#TARGETS START ==> BEFORE (duration) & WITH (start)
	if scope in ['before_any', 'with_any', 'before_all', 'with_all']:#On ne génère la lisque que si elle est utilisée
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
	