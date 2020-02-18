# %% LIBRAIRIE
import argparse
import logging
import json
import os

#import modules.Handlings

# %% LOGGER
logging.basicConfig(
    level= logging.INFO, 
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger("pas-modelling")

# %% MAIN
def main(service, call) :
    '''
    Appelle les modules listés dans Settings pour le Service appeler, leurs passant successivement l'object de Call (transformé par chaque module).
    '''
    os.system("clear") 
    logger.warning("Begining funkyPAS")
    
    # INITIALISATION
    settings = load("./settings.json")
    modulesSequence =  settings["service"][service]

    # PROCESSING
    pas = call

    for module_i in modulesSequence : #TODO ajouter des assert etc
        logger.warning(f"Calling module {module_i}") 
        exec('from modules.' + module_i + " import " + module_i , locals(), globals()) #FIXME donner les droits en globals ? Vérifier de quoi il retourne
        pas = eval(module_i + "(pas, settings['modules_settings'][module_i])")
    
    logger.warning("Closing funkyPAS") 

# %% UTILITIES
def load(full_path):
    with open(full_path) as file :
        return json.load(file)

# %% SHELL
if __name__ == "__main__" :
    parser = argparse.ArgumentParser(description="Process executable options.")
    
    # parser.add_argument(
    #     "--moduleSequence", nargs="+", type=str, help="Steps numbers to execute.",
    # ) #TODO: pouvoir passer la liste des modules ET/OU le path du fichier de conf (défaut racine)
    
    # parser.add_argument(
    #     "-sp", "--settingsPath", default="./settings.json", type=str, help="Path to the json file containing settings"
    # ) TODO voir précédent

    # parser.add_argument(
    #     "-ov", "--outputVerbose", default="normal", type=str, help="restricted: only valid records in output.\n normal (default value); balanced output.\n extended: every processing logs insered into output. Use for setting issues identification. May generate trouble for output conversion to graph"
    # ) TODO: pouvoir passer la liste des modules à la place du fichier de conf ?

    # parser.add_argument(
    #     "--monitor", default=False, action="store_true", help="Start monitoring server"
    # )

    parser.add_argument(
        "--call",
        nargs='?', 
        default="{'call_key':'call_value}", 
        help="Données initiales (info pr call à l'IH)"
    )
    
    parser.add_argument(
        "-s", "--service", 
        nargs='?',
        default="energy_consumption_assessment", 
        help="Spécifie le service du PAS appellé."
    )

    args = parser.parse_args()

    main(args.service, args.call)#args.moduleSequence, args.outputVerbose, args.settingsPath)


# %%
