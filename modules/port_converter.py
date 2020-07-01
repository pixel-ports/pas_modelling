import json


def main(HANDLINGS, PORT, LOGS, SETTINGS, module_name) :
	'''
	Transform odl port's parameters to the proper data-model.
	'''
	#INITIALISATION
	LOGS.append(f"==== {module_name}  ====")


	#RULES
	#	CONTENTS (& ASSIGNATIONS)
	PORT['Contents'] = {}
	for content in PORT['rules']['cargoes_categories']:
		PORT['Contents'].update({
			content['ID']: {
				'label': content.get('label', content['ID']),
				'comment': content.get('comment', "No value"),
				'handling_type': content.get('handling_type', "No value"),
				'group': content.get('segment', "No value"),
				'unit': content.get('unit', "No value"),
				'typical_min_amount': content.get('typical_amount_range', [None, None])[0],
				'typical_man_amount': content.get('typical_amount_range', [None, None])[1],
				'Suitable_SCs':[]
			}
		})
		for assigned_SC in content['assignation_preference']:
			PORT['Contents'][content['ID']]['Suitable_SCs'].append({
				'supply_chain_ID': assigned_SC['supply_chain_ID'],
				'restrictions': {
					'direction': assigned_SC['direction'],
					'dock_ID': assigned_SC['dock_ID'],
					'amount_min': None,
					'amount_max': None
				}
			})
	#	TIMETABLES (ex SHIFTWORKS)
	PORT['Timetables'] = PORT['rules']['shiftworks'] #Déjà un dict par parsing dans le requester
	# for shiftwork in PORT['rules']['shiftworks']:
	# 	PORT['Shiftworks'].update({shifwork['ID']: shifwork })
	#	PRIORITIES
	PORT['Priorities'] = PORT['rules']['priority'] #Il n'y a qu'une séquence de priority
	#	CLEANNING
	del PORT['rules']

	#SUPPLYCHAINS
	#PORT['Supplychains'] = {SC['ID']: PORT['supplychains']} #FIXME Prb dans le format d'enregistrement des SC depuis la GUI vers l'IH, avec une étape intermédiaire inconnue par l'OT
	PORT['Supplychains'] = {SC['ID']: SC
		for SC in PORT['supplychains'] #Devrait être un array
	}
	del PORT['supplychains']
	<<Faire aussi les modifs suivante (en fait changer le nom de la clé)
	#SUPPLY-CHAINS ==> SUPPLYCHAINS
	for sc in PORT['supplychains']:
		PORT['Supplychains'].update({
			sc['ID']: {
				
			}
			"operations_list": sc[]
	"steps_list": [ >"Operations": [
		"category":>"tag":
		
	#CLOSSING
	#LOGS.append(f"====> {module_name} ENDS <====")
	return (HANDLINGS, PORT, LOGS, SETTINGS)


#=========================================================================
