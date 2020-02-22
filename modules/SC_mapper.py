import json
import jsonschema
import logging

logger = logging.getLogger("SC_mapper")


def SC_mapper(pas, module_settings) :
	'''
	handling --> handling + [SC]

	Add to each handling an array of suitable SupplyChains (deduced from parameters "content_type").
	Optionnal filtration can be enabled into Setting
	'''
	logger.warning("Starting")


<<Refaire comme pr convertiseur
	# ASSIGNATION SC 
	handling_withoutSC = 0
	for handling in pas["state"] :
		#handling["supplychains"] = listing_validSC(handling, pas['parameters']['RULES']['content_type_list'], module_settings)
		for content_type in pas['parameters']['RULES']['content_type_list'] :
			if handling["content_type"] == content_type["content_type_ID"] :
				for candidat in content_type["assignation_preferences"] :
					if testing_restrictions(handling, candidat["restrictions"], module_settings["restrictions"]) :
						handling.get("supplychains", "[]").append(candidat["supply_chain"])
					#else #TODO ajout
		# ASSIGNATION SC DEFAUT #Imperativement en dernière étape pour garantir le défault comme dernier choix
		#TODO si SC default existe : liste.append(ref défault)
		

		if len(handling["supplychains"]) == 0:
			#TODO Transférer ce handling de handlings dans rejected_handlings
			handling_withoutSC +=1
	
	# Contrôle de la liste finale
		# Ecarter les handling
		# Prendre uniquement la premiere si option passée<< non ça c'est fait par le suivant
		
	# ASSIGNATION SC DEFAUT
	# (dans tous les cas), on ajoute en dernier dans l'array la SC du handling type
	# AVANT désactiver le transfert des len(handling["supplychains"]) == 0 vers 
	# si SC default existe : liste.append(ref défault) (si non  log)
	# Attention, désactiver le transfert des
		
	logger.warning("Ending")
	#print(candidat_SCs)
	return pas

def calculating_duration(pas, module_settings) :
	return #TODO


#=====================================================
def listing_validSC(handling, RULES_content_type, module_settings): #Pourrait être converti en une nested list comprehension
	
	matching_SC = [] 
	for content_type in RULES_content_type :
		if handling["content_type"] == content_type["content_type_ID"] :
			for candidat in content_type["assignation_preferences"] :
				if testing_restrictions(handling, candidat["restrictions"], module_settings["restrictions"]) :
					matching_SC.append(candidat["supply_chain"])
				#else #TODO ajouter une information dans les logs (l'users doit pouvoir retrouver que des cas ont été écartés par cette filtration (faire un diff de len() ?))
	return matching_SC

def testing_restrictions(handling, candidat_restrictions, settings_restrictions): 
	'''Test a handlings against a candidat, return False if does not meet every requirements
	(intersection of {enabled restrictions in settings} and {existing requirement into candidat})
	NB: a requirement not present into candidat description is considered as succefully passed
	'''#Variante, mettre une clé pour activer/désactivé (en gardant la valeur) pour candidat_restrictions ?

	if (settings_restrictions["direction"] #Bool true pr enabled
		and ("direction" in candidat_restrictions) #and  len(candidat_restrictions["direction"]) > 0  #on ne veut vraiment empecher un array vide
		and handling["handling_direction"] not in candidat_restrictions["direction"] 
	) : 
		return False
	if (settings_restrictions["dock"] 
		and ("dock" in candidat_restrictions) 
		and handling["handling_dock"] not in candidat_restrictions["dock"] 
	) : 
		return False
	if (settings_restrictions["amount_min"] 
		and("amount_min" in candidat_restrictions) 
		and handling["content_amount"] < candidat_restrictions["amount_min"] 
	) : 
		return False
	if (settings_restrictions["amount_max"] 
		and("amount_max" in candidat_restrictions) 
		and handling["content_amount"] > candidat_restrictions["amount_max"] 
	) : 
		return False
	return True