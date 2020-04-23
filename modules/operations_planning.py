def process(HANDLINGS, PORT, LOGS, SETTINGS, module_name) :
	'''
	For each handling, assign an operation.
	On operation have :
	- start TS, 
	- duration 
	- end TS
	- ressources use (list)
	NB IDéalement, on sort le scheduling (uniquement des durées d'opération) ET la gestion de la concurence d'accès ressource.
	Alternative : avoir la prise en compte de la concurence comme un argument ds settings
	'''
	#INITIALIZATION
	LOGS.append(f"===== {module_name} STARTS =====")


	#OPERATIONS PLANNIFICATION
	#operation = theoritical SC processing unit
	#activitie = practical handling processing unit 
	Operations_rejection = []
	for handling in HANDLINGS:
		
		#OPERATIONS RETRIVING
		(Operations_success, Operations_list) = get_SC_operations(handling, PORT["Supplychains"])
		if not Operations_success :
			Operations_rejection.append(handling)
		
		#ACTIVITIES PLANNING 
		Activities_list = []
		
		for operation in Operations_list:
			activity = {
				"ID": operation.get("ID"),
                "label": operation.get("label"),
                "comment": operation.get("comment"),
                "category": operation.get("category"),
                "start_TS": None,
				"end_TS": None,
				"duration": None,
				"Ressources_list": operation["work"].get("machines")
			}
			# Delay
			if operation["scheduling"]["duration"].get("nature") == "delay":
				activity["duration"] = operation["scheduling"]["duration"].get("value")
			
			# Cargo
			if operation["scheduling"]["duration"].get("nature") in ["cargo_tons", "cargo_%"]:
				net_throughput = get_net_throughput(handling["content_type"], operation.get("work"), PORT["Resources"]["machines"])
				net_amount = get_net_amount(handling['content_amount'], operation["scheduling"]["duration"])
				activity["duration"] = net_amount / net_throughput

			# Dependency
			#CONTROLE DE BOUCLE INFINIE #TODO
			#while len(Activities_list) < len(Operations_list): + Si pas d'avancée
			# 
			
			Activities_list.append(activity)

			
	LOGS.append(f"Number of handling that does not have operations: {len(Operations_rejection)}")
	if len(Operations_rejection) > 0:
		LOGS.append({"List of rejection": Operations_rejection})

	#CLOTURE	
	LOGS.append(f"===== {module_name} ENDS =====")
	return HANDLINGS, PORT, LOGS, SETTINGS

#=====================================================
def get_SC_operations(handling, Supplychains):
	'''
	Parcours la liste des SC du handling, jusqu'à trouver une correspondance dans PORT["Supplychains"] dont on renvois la liste des steps
	'''
	Operations = []
	success = False

	while success == False :
		for handling_sc in handling["supplychains"]:
			for port_sc in Supplychains :
				if port_sc["ID"] == handling_sc:
					Operations = port_sc["steps_list"]
					success = True

	return (success, Operations)

def get_net_throughput(content_type, operation_work, Machines):
	return

def get_net_amount(handling_amount, operation_duration):
	if operation_duration.get("nature") == "cargo_%":
		net_amount = handling_amount * operation_duration.get("value")
	if operation_duration.get("nature") == "cargo_tons":
		net_amount = operation_duration.get("value")
	return net_amount