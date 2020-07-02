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
	

	#SUPPLYCHAINS
	PORT['Supplychains'] = {}
	for sc in PORT['supplychains']:
		operations_list = []
		for step in sc['steps_list']:
			operation = {
				step['ID']: {
					"label": step['label'],
					"comment": step['comment'],
					"tag_list": [step['category']],
					"scheduling": step['scheduling'],
					"ressources_uses": {
						"ressources_IDs": step['work'].get('machines'),
						"nature": step['work'].get('nature'),
						"distance": step['work'].get('distance')
					}
				}
			}
			operations_list.append(operation)

		PORT['Supplychains'].update(
			{
				sc['ID']: {
					'label': sc['label'],
					'comment': sc['comment'],
					'operations_list': operations_list
				}
			}
		)

	
	#RESOURCES
	PORT["Resources"] = {} #On remerge en un seul type d'entité, mais avec une clé de nature
	for nature in PORT['resources'].keys():
		for resource in PORT['resources'][nature]:
			PORT["Resources"].update({
				resource.get('ID'): {
					'label': resource.get('label'),
					'comment': resource.get('comment'),
					'nature': nature,
					'type': resource.get('type'),
					'timetable_ID': resource.get('shift_ID'),
					'throughput': resource.get('throughput'),
					'Energies_consumptions': resource.get('consumptions')
				}
			})

	# for area in PORT['resources'].get('areas'):
	# 	Resources.update({
	# 		area['ID']: {
	# 			'label': area['label'],
	# 			'comment': area['comment'],
	# 			'nature': "area",
	# 			'type': area['type'],
	# 			'timetable_ID': area['shift_ID'],
	# 			'throughput': area['throughput'],
	# 			'Energies_consumptions': area['consumptions'],
	# 			}
	# 		}
	# 	)
	# for machine in PORT['resources'].get('machines'):
	# 	Resources.update({
	# 		machine['ID']: {
	# 			'label': machine['label'],
	# 			'comment': machine['comment'],
	# 			'nature': "machine",
	# 			'type': machine['type'],
	# 			'timetable_ID': machine['shift_ID'],
	# 			'throughput': machine['throughput'],
	# 			'Energies_consumptions': machine['consumptions'],
	# 			}
	# 		}
	# 	)
	

		
	#CLOSSING
	#	CLEANNING
	del PORT['rules']
	del PORT['supplychains']
	del PORT['resources']

	return (HANDLINGS, PORT, LOGS, SETTINGS)


#=========================================================================
