#import collections

def process(HANDLINGS, PORT, LOGS, SETTINGS, module_name) :
	'''
	handling --> handling + [SC]

	Add to each handling an array of suitable SupplyChains (deduced from parameters "RULES>content_type_list").
	Optionnal filtration can be enabled into Setting
	'''
	# COMMENT
	# Un code avait été fait pr les DM mis à jour. Cette base est modifiée (passe en commentaires) pr être compatible avec les anciens DM utilisés pr la GUI
	
	#INITIALIZATION
	LOGS.append(f"<==== {module_name} STARTS ====>")
	Unreconized_content_types = []
	Duplicated_content_types = []
	Requirements_rejection = []
	Default_SC_assignations = []
	Unretrieved_SCs = []
	nb_handlings_in = len(HANDLINGS)

	#PROCESSING
	for handling in HANDLINGS :
		# ASSIGNATION SC PAR CONTENT TYPE
		#	MATCHING CT:
		candidatSC_nestedList = []
		for content in PORT["Contents"]:
			if content["ID"] == handling["content_type"]:
				for candidat_assignation in content["assignation_preference"]:
					if candidat_assignation["dock_ID"] == handling["handling_dock"] and candidat_assignation["direction"] == handling["handling_direction"]:
						candidatSC_nestedList.append(candidat_assignation["supply_chain_ID"])
		# candidatSC_nestedList = [content["assignation_preference"].get("Suitable_SCs", [])
		# 	for content in PORT["Contents"] 
		# 	if content["ID"] == handling["content_type"]
		# ]
		if len(candidatSC_nestedList) == 0 : #NB même si pas de SC, le len sera de 1 avec un CT qui match 
			Unreconized_content_types.append(handling["content_type"]) 
		elif len(candidatSC_nestedList) > 1 : #NB cas qui ne devrait pas exister si PORT est propres
			Duplicated_content_types.append(handling["content_type"])
		
		handling["Supplychains"]= candidatSC_nestedList
		#	SUITABLE SC:
		# handling["Supplychains"] = []
		if len(candidatSC_nestedList) > 0 :
			
			# Rejections=[]
			# for candidat_SC in [candidat_SC for suitable_CT in candidatSC_nestedList for candidat_SC in suitable_CT]:
			# 	requirement_success, requirement_Messages = test_SC_requirements(handling, candidat_SC["restrictions"], SETTINGS["modules_settings"][module_name]["restrictions"])
			# 	if requirement_success:
			# 		handling["Supplychains"].append(candidat_SC["supplychain"])
			#LOGS DES REJETS
				# else:
				# 	Rejections.append({
				# 		"Rejected SC": candidat_SC["supplychain"],
				# 		"Causes": requirement_Messages
				# 	})
			if len(handling["Supplychains"]) == 0: #On ne log qu'a posteriori, si l'handling n'a pas recut de SC du fait des requirements
				Requirements_rejection.append(
					{
						"Handling": handling,
						# "Rejections":Rejections
					}
				)

		# ASSIGNIATIONS SC PAR DEFAULT 
		if SETTINGS["modules_settings"][module_name]["default_SC"]:
			if len(handling["Supplychains"]) == 0: 
				default_success, default_sc = assigne_default_SC(handling, PORT["Contents"])#FIXME non implémenté
				if default_success:
					handling["Supplychains"].append(default_sc)
					Default_SC_assignations.append(handling)

		# REMOVE HANDLING'S SC THAT ARE NOT DEFINED IN PORT["Supplychains"]
		for sc in handling["Supplychains"]:
			if sc not in [supplychain["ID"] for supplychain in PORT["Supplychains"]]:
				handling["Supplychains"].remove(sc)
				if sc not in set(Unretrieved_SCs):
					Unretrieved_SCs.append(sc)
				
				

	# REJET DES HANDLINGS SANS SC
	Unassigned_handlings = [handling
			for handling in HANDLINGS
			if len(handling["Supplychains"]) == 0
		]
	if SETTINGS["modules_settings"][module_name]["discart_unassigned"]:
		for handling in Unassigned_handlings:
			HANDLINGS.remove(handling) #Attention, fiabilité discutable s'il y a des doublons (mais devraient être en double aussi dans la liste mère)


	#LOGS
	#	Duplicated_content_types
	LOGS.append(f"Number of duplicated content type: {len(set(Duplicated_content_types))}") #Impacte l'assignation a travers l'affectation de l'ordre des SC résultantes
	if len(set(Duplicated_content_types)) > 0:
		LOGS.append({"List of duplicated content type": set(Duplicated_content_types)})

	#	Unreconized_content_types
	LOGS.append(f"Number of handling with unreconized content type: {len(Unreconized_content_types)}")
	if len(set(Unreconized_content_types)) > 0:
		LOGS.append({"List of unreconized content type": set(Unreconized_content_types)}) #TODO ajouter le nb d'handlings du sous groupe

	#	Requirements_rejection
	LOGS.append(f"Number of handling that loose matching assignation due to SC requirement: {len(Requirements_rejection)}")
	if len(Requirements_rejection) > 0:
		LOGS.append({"List of requirements rejection": Requirements_rejection})

	#	Default SC assignation
	LOGS.append(f"Number of handling that get a default assignation: {len(Default_SC_assignations)}")
	if len(Default_SC_assignations) > 0:
		LOGS.append({"List of handlings with a default SC assignation": Default_SC_assignations})

	#	Unretrieved SC
	LOGS.append(f"Number of supplychains not retrieved in port's supplychains collection: {len(Unretrieved_SCs)}")
	if len(Unretrieved_SCs) > 0:
		LOGS.append({"List of unretrieved supplychains": Unretrieved_SCs})

		#	Discarted handlings
	LOGS.append(f"Number of handling that did not get any SC assignation : {len(Unassigned_handlings)}")
	LOGS.append(f'Deleting non assigned handling (option in settings): {SETTINGS["modules_settings"][module_name]["discart_unassigned"]}')
	if len(Unassigned_handlings) > 0:
		LOGS.append({"List of handlings without any SC assignation": Unassigned_handlings})

	# Proportion
	LOGS.append(f"Proportion of unassigned: {round((len(Unassigned_handlings)/nb_handlings_in)*100, 2)}% ({len(Unassigned_handlings)} from the inital {nb_handlings_in})")


	#CLOTURE	
	LOGS.append(f"====> {module_name} ENDS <====")
	return HANDLINGS, PORT, LOGS, SETTINGS

#=====================================================
def test_SC_requirements(handling, assignation_restrictions, settings_restrictions): 
	'''Test a handlings against a candidat assignation, return False if does not meet every requirements
	(intersection of {enabled restrictions in settings} and {existing requirement into assignation})
	NB: a requirement key not present into assignation description is considered as succefully passed but a requirement key present with an empty value will reject every handling
	'''#Variante, mettre une clé pour activer/désactivé (en gardant la valeur) pour assignation_restrictions ?
	Messages = []

	if (settings_restrictions["direction"] #Etat de l'option de filtre dans settings
		and ("direction" in assignation_restrictions) #Existance de la clé dans l'assignation
		and handling["handling_direction"] not in assignation_restrictions["direction"] #Adéquation de l'handling
	) : 
		Messages.append(f"Unmatch on direction")
	
	if (settings_restrictions["dock"] 
		and ("dock" in assignation_restrictions) 
		and handling["handling_dock"] not in assignation_restrictions["dock"] 
	) : 
		Messages.append(f"Unmatch on dock")
	
	if (settings_restrictions["amount_min"] 
		and("amount_min" in assignation_restrictions) 
		and handling["content_amount"] < assignation_restrictions["amount_min"] 
	) : 
		Messages.append(f"Unmatch on amount_min")
	
	if (settings_restrictions["amount_max"] 
		and("amount_max" in assignation_restrictions) 
		and handling["content_amount"] > assignation_restrictions["amount_max"] 
	) : 
		Messages.append(f"Unmatch on amount_max")
	
	if len(Messages) > 0:
		success = False
	else:
		Messages = "SC requirements filtering: successfull"
		success = True
	return (success, Messages)

def assigne_default_SC(handling, Assignations):#FIXME
	default_SC = "SC1"

	if default_SC is None:
		success = False
	else :
		success = True

	return (success, default_SC)
