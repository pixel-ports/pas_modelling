# INSTANTIATION SC
SC_desription = [
	{
		"ID":"op0",
		"start":{
			"dependencies" : []
		},
		"end":{
			"dependencies": []
		}
	},
	{
		"ID":"op1",
		"start":{
			"dependencies" : ["op2_start"]
		},
		"end":{
			"dependencies": []
		}
	},
	{
		"ID":"op2",
		"start":{
			"dependencies" : ["op3_end"]
		},
		"end":{
			"dependencies": []
		}
	},
	{
		"ID":"op3",
		"start":{
			"dependencies" : []
		},
		"end":{
			"dependencies": []
		}
	}		
]

#CONVERTION GRAPHE
graphe = dict()
for op in SC_desription:
	graphe[op["ID"] + "_start"] = list(set(op["start"].get("dependencies", [])))
	graphe[op["ID"] + "_end"] = list(set(op["end"].get("dependencies", []) + [op["ID"] + "_start"])) #On fonctionne en "forward scheduling": toute fin d'opération dépend du début, mais le début d'une opération ne dépend jamais de sa fin


#RESOLUTION DU GRAPHE

#	INITIALISATION
unchecked = list(graphe.keys())
checked = []
loop_detected = False


def resolve_TS(node_ID):
	#En l'abscence de boucle, peut on assurer de parcourir tout le graphe?
	SC_desription[node_ID]


def graph_runner(node_ID, node_dependencies):
	stack.append(node_ID)
	global loop_detected
	if loop_detected:
		return
	
	for parent_ID in node_dependencies:
		# Détection d'une boucle dans le graphe
		if parent_ID in stack:
			loop_detected = True 
			return
		# Appel récursif sur les dépendences de l'opération
		if parent_ID in unchecked:
			graph_runner(parent_ID, graphe[parent_ID])
	# Passage de l'opération au statut de vérifiée
	resolve_TS(node_ID)
	checked.append(node_ID)
	

#	RUN
for (node_ID, node_dependencies) in list(graphe.items()):
	if node_ID in unchecked:
		stack = []
		graph_runner(node_ID, node_dependencies)
	if loop_detected:
		break

#	AFFICHAGE RESULTAT
if loop_detected:
	print("PRB, boucle détectée !")

elif loop_detected == False:
	print("Ok, pas de boucle détectée")
else:
	print("Autre cas. Etrange")
