	
def main(HANDLINGS, PORT, LOGS, SETTINGS, module_name) :
	'''
	handling --> handling + [SC]
	Add to each handling an array of suitable SupplyChains (deduced from parameters "RULES>content_type_list").
	Optionnal filtration can be enabled into Setting
	'''
#INITIALIZATION
	LOGS.append(f"==== {module_name}  ====")
	Valid_items = []
	Invalide_items = [] 
	Errors = [] #template pr un item error: {"type": None,"item": None,"handling": None,"message": f''}
	nb_handling_start = len(HANDLINGS)
#PROCESSING
	for handling in HANDLINGS :
	#ASSIGNATION SC PAR CONTENT TYPE
	#	RETRIVE ASSIGNMENT
		Candidat_assignments = PORT["contentType"].get(handling["content_type"],{}).get('suitable_assignations')
		if Candidat_assignments is None: # len(Candidat_assignments) == 0
			handling['status'] = ('HS', {
				"type": "Unknown content type",
				"item": handling["content_type"],
				"message": f''
			})
		elif len(Candidat_assignments) == 0: #TODO oui c'est différents, mais un peu redondant quand même
			handling['status'] = ('HS',	{
				"type": "No assignment candidat",
				"item": PORT["contentType"].get(handling["content_type"],{}).get('suitable_assignations'),
				"message": f''
			})
	#	TEST ASSIGNMENTS
		else:
			Valided_assignment = []
			Unvalided_assignment = []
			for candidat_assignment in Candidat_assignments:
				success, data = test_assignment_requirements(handling, candidat_assignment.get("restrictions"), SETTINGS["restrictions"])
				if success:
					Valided_assignment.append(candidat_assignment)
				else:
					Unvalided_assignment.append(data)
			if len(Valided_assignment) > 0:
				handling['status'] = ('OK', None) #FIXME ce champs est trompeur
				handling["assigned_SC_ID"] = Valided_assignment[0]["SC_ID"]  #On prend uniquement la première SC. NB ce choix est discutable, on pourrait prendre toutes les compatibles pr ouvrir le champs à d'autres modules (prochaine version ?)
				Valid_items.append(handling)
			else:
				handling['status'] = ('HS',	{
				"type": "No valid assignements",
				"item": "None of the candidat assigments was suitable.",
				"message": f'Detail: {Unvalided_assignment}'
			})
	# ASSIGNIATIONS SC PAR DEFAULT 
		if SETTINGS["default_SC"]: #FIXME crash si l'option est activée
			LOGS.append("User settings bypassed, option desactivated")
			# if len(handling.get("assigned_SC_ID", [])) == 0: 
			# 	success, data = assign_default_SC(handling, PORT["contentType"])#FIXME non implémenté
			# 	if success:
			# 		handling["assigned_SC_ID"] = data
			# 		handling['status'] = ('OK',	{
			# 			"type": "Default supplychain assignment",
			# 			"item": "None of the candidat assigments was suitable.",
			# 			"message": f'Detail: {Unvalided_assignment}'
			# 		})
	# REMOVE HANDLING'S SC THAT ARE NOT DEFINED IN PORT["Supplychains"]
		# for sc in handling["Supplychains_IDs"]:
		# 	if sc not in [supplychain["ID"] for supplychain in PORT["Supplychains"]]:
		# 		handling["Supplychains_IDs"].remove(sc)
		# 		if sc not in set(Unretrieved_SCs):#FIXME non implémenté
		# 			Unretrieved_SCs.append(sc)
#CLOTURE
	#	REJET DES HANDLINGS SANS SC
	Unassigned_handlings = [handling for handling in HANDLINGS if "assigned_SC_ID" not in handling]  #Garantir la présence du champs et tester sur len, ou tester présence ?
	if SETTINGS["discart_unassigned"]:
		for handling in Unassigned_handlings:
			HANDLINGS.remove(handling) #Attention, fiabilité discutable s'il y a des doublons (mais devraient être en double aussi dans la liste mère)	
	
	#	LOGS
	Invalide_items = [handling for handling in HANDLINGS if handling['status'] == 'HS']
	Errors_synthesise = {}
	for error in Errors:
		Errors_synthesise.setdefault(error['type'], {})
		Errors_synthesise[error['type']].setdefault(error['item'], {
			"number of occurences": 0, 
			"message": error["message"],
			"involved handlings": []
		})
		Errors_synthesise[error['type']][error['item']]["involved handlings"].append(error["handling"])
		Errors_synthesise[error['type']][error['item']]["number of occurences"] = len(Errors_synthesise[error['type']][error['item']]["involved handlings"])
		# Errors_synthesise['Invalide_handlings'].append(error['handling'])
	
	LOGS.append(f"Handlings with assigned SC: {len(Valid_items)} ({nb_handling_start} records where passed, {len(Unassigned_handlings)} records discarded)") #FIXME mauvaise manière de calculer, on ne garantie pas la cohérence des chiffres donnés
	if (nb_handling_start != len(Valid_items) + len(Unassigned_handlings)) | (len(Valid_items) != len(HANDLINGS)): 
		raise Exception('Inconsistency between number handlings ok and not ok') #FIXME

	if len(Unassigned_handlings) > 0:
		LOGS.append({"Details": Errors_synthesise}) #FIXME
	return HANDLINGS, PORT, LOGS

#=====================================================
def test_assignment_requirements(handling, assignment_restrictions, settings_restrictions): 
	'''Test a handlings against a candidat assignation, return False if does not meet every requirements
	(intersection of {enabled restrictions in settings} and {existing requirement into assignation})
	NB: a requirement key not present into assignation description is considered as succefully passed but a requirement key present with an empty value will reject every handling
	'''#Variante, mettre une clé pour activer/désactivé (en gardant la valeur) pour assignment_restrictions ?
	success = None
	data = None

	try:
		Messages = []

		if (settings_restrictions["direction"] #Etat de l'option de filtre dans settings
			and ("direction" in assignment_restrictions) #Existance de la clé dans l'assignation
			and handling["handling_direction"] not in assignment_restrictions["direction"] #Adéquation de l'handling
		) : 
			Messages.append(f"Unmatch on direction")
		
		if (settings_restrictions["dock"] 
			and ("dock" in assignment_restrictions) 
			and handling["handling_dock"] not in assignment_restrictions["dock"] 
		) : 
			Messages.append(f"Unmatch on dock")
		
		if (settings_restrictions["amount_min"] 
			and("amount_min" in assignment_restrictions) 
			and handling["content_amount"] < assignment_restrictions["amount_min"] 
		) : 
			Messages.append(f"Unmatch on amount_min")
		
		if (settings_restrictions["amount_max"] 
			and("amount_max" in assignment_restrictions) 
			and handling["content_amount"] > assignment_restrictions["amount_max"] 
		) : 
			Messages.append(f"Unmatch on amount_max")
		
		if len(Messages) == 0:
			success = True
		else:
			success = False
			data = { 
				"type": "Unvalid assignment",
				"item": assignment_restrictions, #NB inverser avec 
				"handling": handling,
				"message": f'Details: {Messages}'
			}
		
	except Exception as error:
		success = False
		data = { 
			"type": "Error occured durint assignation test",
			"item": assignment_restrictions,				
			"handling": handling,
			"message": f'{error}'
		}

	return success, data


def assign_default_SC(handling, Assignations):#FIXME
	default_SC = "sc_1"

	if default_SC is None:
		success = False
	else :
		success = True

	return (success, default_SC)
