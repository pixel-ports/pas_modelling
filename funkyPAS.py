#===============================================================
'''
# SYNOPSIS

## PURPOSE
Refonte du PAS builder dans une approche plus fonctionnelle. En effet on ne procede qu'à une succession de transformations identique pour tous les enregistrement, dans un flux univoque/directionnel.
Handlings ==> Operations ==> Activités ==> Consommations ==> Emissions

## STATUT

V0.1

### TODO
Tout

'''
#===============================================================

import argparse
import logging
import json
import modules.InputsCollector
import modules.Handlings



logging.basicConfig(
    level= logging.INFO, 
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger("pas-modelling")


#=====================================================
def main(call) :
    '''
    Prends un dictionnaire unique (PAS), et le fait transformer successivement par chaque module selon la séquence donnée.
    '''
    logger.warning("Begining funkyPAS")
    
    PAS = call

    # TODO ici l'idée initiale était de dérouler l'application d'une liste de modules passé en argument. Pr le moment on va faire en dur.
    # moduleSequence = [ #FIXME c'est moche en dur comme ça, mais c'est plus pratique pr le moment
    #     "Inport_Inputs", 
    #     "Handlings", 
    #     "Operations", 
    #     "Activities", 
    #     "Consumptions", 
    #     "Export_output"
    # ]

    # for module_i in moduleSequence : #TODO ajouter des assert etc
    #     logger.warning(f"Calling module {module_i}") 
    #     exec('import ' + module_i, locals(), globals())
    #     PAS = module_i(PAS)
    
    PAS = InputsCollector(PAS)
    PAS = Handlings(PAS)
    #PAS = Operations(PAS)
    #PAS = Activities(PAS)
    #PAS = Consumptions(PAS)
    #PAS = Export_output(PAS)

    print(PAS)
    logger.warning("Closing funkyPAS") 
    
#Subtools
def get_json(path, file, suffixe):
    with open(path + file + suffixe) as file :
        return json.load(file)
    
#=====================================================
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
        "--call", default=None, action="store_true", help="Body du call au modèle"
    )
    args = parser.parse_args()

    main(args.call)#args.moduleSequence, args.outputVerbose, args.settingsPath)
