# %% LIBRAIRIE
import argparse
import logging
import json
import os

os.system("clear") 
logging.basicConfig(
	level= logging.INFO, 
	format='%(name) -8s %(message)s')
logger = logging.getLogger("funkyPAS (main)")

# %% MAIN
def main(pipeline, call) :
	'''
	Appelle les modules listés dans Settings pour le pipeline appeler, leurs passant successivement l'object de Call (transformé par chaque module).
	#TODO: regrouper en grandes étapes de transformation:
	call --> handlings
	handlings --> operations
	operations --> consumptions
	operations --> activities
	#TODO homogénéiser les noms :
	•UPPERCASE ou UPPER_CASE pour les constantes 
	•TitleCasepour les classes 
	•camelCasepour les fonctions, les m ́ethodes et les interfaces graphiques 
	•lowercaseoulower_casepour tous les autres identifiants.
	'''
	logger.warning("Starting")
	
	# INITIALISATION
	with open("./settings.json") as file :
		SETTINGS = json.load(file)

	MODULES_SEQUENCE = SETTINGS["pipelines"][pipeline]
	
	pas = {
		"state": call,
		"parameters": {},
		"log": {}
	}


	# PROCESSING
	for module_i in MODULES_SEQUENCE : #TODO ajouter des assert/try pour empécher tout crash salle
		logger.warning(f"Calling module {module_i}") 
		exec('from modules.' + module_i + " import " + module_i , locals(), globals()) #FIXME donner les droits en globals ? Vérifier de quoi il retourne
		pas = eval(module_i + "(pas, SETTINGS['modules_settings'][module_i])")
	
	
	logger.warning("Ending")
	

# %% SHELL
if __name__ == "__main__" :
	parser = argparse.ArgumentParser(description="Process executable options.")
	
	# parser.add_argument(
	#	 "--moduleSequence", nargs="+", type=str, help="Steps numbers to execute.",
	# ) #TODO: pouvoir passer la liste des modules ET/OU le path du fichier de conf (défaut racine)
	
	# parser.add_argument(
	#	 "-sp", "--settingsPath", default="./settings.json", type=str, help="Path to the json file containing settings"
	# ) TODO voir précédent

	# parser.add_argument(
	#	 "-ov", "--outputVerbose", default="normal", type=str, help="restricted: only valid records in output.\n normal (default value); balanced output.\n extended: every processing logs insered into output. Use for setting issues identification. May generate trouble for output conversion to graph"
	# ) TODO: pouvoir passer la liste des modules à la place du fichier de conf ?

	# parser.add_argument(
	#	 "--monitor", default=False, action="store_true", help="Start monitoring server"
	# )

	parser.add_argument(
		"--call",
		nargs='?', 
		default= None, 
		help="Données initiales (info pr call à l'IH)"
	)
	
	parser.add_argument(
		"-p", "--pipeline", 
		nargs='?',
		default="energy_consumption_assessment", 
		help="Spécifie le pipeline du PAS appellé."
	)

	args = parser.parse_args()

	main(args.pipeline, args.call)#args.moduleSequence, args.outputVerbose, args.settingsPath)
