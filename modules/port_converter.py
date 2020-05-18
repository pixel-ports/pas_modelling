import json


def process(HANDLINGS, PORT, LOGS, SETTINGS, module_name) :
	'''
	Transform odl port's parameters to the new DM.
	'''
	#INITIALISATION
	LOGS.append(f"<==== {module_name} STARTS ====>")


	#RULES ==> ASSIGNATIONS
	# PORT["Assignations"] = PORT["Assignations"]['cargoes_categories']
	# for cargo_type in PORT["Assignations"]:
	# 	cargo_type = {
	# 		"content_type_ID": cargo_type["ID"],
	# 		"handling_type":cargo_type["segment"],
	# 		"Suitable_SCs": [
	# 			{
	# 				"supplychain": cargo_type["assignation_preference"][0]["supply_chain_ID"],
	# 				"restrictions": {
	# 					"direction": cargo_type["assignation_preference"][0]["direction"],
	# 				}
	# 			}
	# 		]
	# 	}
	PORT["Contents"] = PORT["RULES"]['cargoes_categories']
	
	#SUPPLY-CHAINS ==> SUPPLYCHAINS
	# for sc in PORT["Supplychains"]:
	# 	sc = {
	# 		"operations_list": sc[]
	# "steps_list": [ >"Operations": [
	# 	"category":>"tag":
		
	#CLOSSING
	LOGS.append(f"====> {module_name} ENDS <====")
	return (HANDLINGS, PORT, LOGS, SETTINGS)


#=========================================================================
