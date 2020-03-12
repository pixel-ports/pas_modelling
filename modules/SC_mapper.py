import json
import jsonschema
import logging

logger = logging.getLogger("SC_mapper")


def SC_mapper(PAS, module_settings) :
	'''
	handling --> handling + [SC]

	Add to each handling an array of suitable SupplyChains (deduced from parameters "RULES>content_type_list").
	Optionnal filtration can be enabled into Setting
	'''
	# logger.warning("Starting")


	# ASSIGNATION SC DU CONTENT TYPE
	for handling in PAS["state"] :
		#AJOUT DES SC QUI MATCHENT
		#VARIANTE (boucle)
		for content_type in PAS['parameters']['RULES']['content_type_list'] :
			if content_type["content_type_ID"] == handling["content_type"] : 
				for candidat_SC in content_type["suitable_SC"] :
					if testing_SC(handling, candidat_SC["restrictions"], module_settings["restrictions"]):
						handling["supplychains"] = [candidat_SC["supplychain"] 
							for candidat_SC in content_type["suitable_SC"]]
		

		'''#VARIANTE (hybride)
		#Matching du content_type
		matching_content_type_list = [content_type for content_type 
			in PAS["parameters"]["RULES"]["content_type_list"] 
			if content_type["content_type_ID"] == handling["content_type"]]

		#Log si content_type en double dans Rules
		if len(matching_content_type_list) >1:
			print(f"\nError, the handling {handling} \n\nmatchs more than one content_type in Rules: \n{matching_content_type_list}\nOnly the first one will be considered") #TODO remplacer par w	arning log
		
		if len(matching_content_type_list) == 1:
			#Extraction des SC du content type
			candidat_SC_list = [content_type["suitable_SC"] for content_type 
				in matching_content_type_list 
				#if len(matching_content_type_list) == 1
				][0] #On ne cherche pas à extraire de SC si la liste est vide
		
			#Assignation des SC si les requirements sont respectés
			for candidat_SC in candidat_SC_list :
				if testing_SC(handling, candidat_SC["restrictions"], module_settings["restrictions"]):
					handling["supplychains"] = candidat_SC["supplychain"]
			# #VARIANTE (list comprehension)
			# handling.setdefault("supplychains", []).append([candidat_SC["supplychain"]
			# 	for candidat_SC in candidat_SC_list[0]#On ne prends que le premier content_type 
			# 	if testing_SC(handling, candidat_SC["restrictions"], module_settings["restrictions"])
			# ])
		'''
		
		'''#VARIANTE (list comprehension)
		matching_content_type_list = [content_type 
			for content_type in PAS['parameters']['RULES']['content_type_list'] 
			if content_type["content_type_ID"] == handling["content_type"]]
		
		if len(matching_content_type_list) == 1 : #c'est cette condition qui est embettante
			handling.setdefault("supplychains", []).append([candidat_SC["supplychain"] 
				for candidat_SC in matching_content_type_list[0]["suitable_SC"] 
				if testing_SC(handling, candidat_SC["restrictions"], module_settings["restrictions"])#[O]
			])
		#Comme finalement on ne s'appuit pas sur len(matching_content_type_list) pr traiter les cas =0,=1 et >1, ne sert à rien et peu lisible)
		'''
	# GESTION DES HANDLINGS SANS SC #Doit couvrir l'ensemble des cas, pas uniquement les handlings sans CT qui match (donc après)
	handlings_ss_SC= [handling 
		for handling in PAS["state"] 
		if len(handling.setdefault("supplychains", []))==0]
	
	print(f"Nb de handlings sans supplychain: {len(handlings_ss_SC)}")
	for handling in handlings_ss_SC :
		print(f'{handling["handling_ID"]}, {handling["handling_type"]}, {handling["content_type"]}')

		#TODO Appliquer une SC par défaut
		# for handling in handlings_ss_SC :
		# 	handling = assigning_default_SC(handling)
		#TODO Rejetter les handling sans SC en log
		# if len(matching_content_type_list) == 0:
		# 	PAS["log"]['rejected_handlings'].append({
		# 		"issue": {
		# 			'invalid_key': {
		# 				"key":"content_type",
		# 				"value":handling["content_type"],
		# 				"comment": "No match with content_type in port's parameters"
		# 			}
		# 		},
		# 		"module":"SC_mapper",
		# 		"handling": handling
		# 	})
		
	# logger.warning("Ending")
	#print(candidat_SCs)
	return PAS

def calculating_duration(pas, module_settings) :
	return #TODO


#=====================================================
def testing_SC(handling, assignation_restrictions, settings_restrictions): 
	'''Test a handlings against a candidat assignation, return False if does not meet every requirements
	(intersection of {enabled restrictions in settings} and {existing requirement into assignation})
	NB: a requirement key not present into assignation description is considered as succefully passed but a requirement key present with an empty value will reject every handling
	'''#Variante, mettre une clé pour activer/désactivé (en gardant la valeur) pour assignation_restrictions ?

	if (settings_restrictions["direction"] #Bool true pr enabled
		and ("direction" in assignation_restrictions) 
		#VARIANTE: and  len(assignation_restrictions["direction"]) > 0  #on autorise un array vide
		and handling["handling_direction"] not in assignation_restrictions["direction"] 
	) : 
		return False #VARIANTE: (False, "Unmatch on direction") #si on veut un tuple avec la raison du refus
	
	if (settings_restrictions["dock"] 
		and ("dock" in assignation_restrictions) 
		and handling["handling_dock"] not in assignation_restrictions["dock"] 
	) : 
		return False #(False, "Unmatch on dock")
	
	if (settings_restrictions["amount_min"] 
		and("amount_min" in assignation_restrictions) 
		and handling["content_amount"] < assignation_restrictions["amount_min"] 
	) : 
		return False #(False, "Unmatch on amount_min")
	
	if (settings_restrictions["amount_max"] 
		and("amount_max" in assignation_restrictions) 
		and handling["content_amount"] > assignation_restrictions["amount_max"] 
	) : 
		return False #(False, "Unmatch on amount_max")
	
	return True #(True, "all restrictions match")
	#Faire un output en vecteur booléen ?

