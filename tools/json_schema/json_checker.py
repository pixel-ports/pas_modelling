"""
=====================================================================
# README

## Current state
v0.2.2

## Purpose
This tool check if a given folder containing identified json are valid against their known json-schema.

## To do
[] Use a conf file instead of hard coded names & paths
[] Faire une vraie gestion des chemins relatifs entre inputs/X et tools/..
[] Faire des logs ouune édition direct ds le fichier qui pose problème
[] Ne pas quitter au premier fichier non présent (mais essayer pr chacun de la liste)


"""


# LIBRAIRIES
import argparse
import json
import jsonschema
from pathlib import Path
import sys

# PRESET JSON NAME
jsonNames_list = [
#    "CARGOES_HANDLING_REQUESTS",
#    "RULES",
    "SUPPLYCHAINS",
#    "RESOURCES"
]

# MAIN
def main(setTestedPath, setScemasPath):

    # Definition des paths :
    ''' 
    Le travail en cours consiste à mieux répondre au cas ou l'user est dans le dossier des json à tester qui l'interesse
    '''
    cwd = Path.cwd()
    if setTestedPath== None :
        tested_folderPath = cwd
        print(f"No path given for tested files (use -stf), current working directory will be use: {cwd}")
    else :
        tested_folderPath = setTestedPath

    if  setScemasPath== None :
        schema_folderPath = "../..//tools/json_checker/json_schemas/"
    else :
        schema_folderPath = setScemasPath


        print(f"No path given for json schema fil (use -ssf), default path will be use: {schema_folderPath}")
    # Check existance des dossiers
    validated_json = []
    
    print("\n---Processing---\n")
    for folder in [("tested files", tested_folderPath), ("validation schema", schema_folderPath)] :
        if not Path(folder[1]).exists() :
            print(f"Issue for {folder[0]}. Verify the given folder path: {folder[1]} was not found. \nNote that you are currently in {cwd}")
            print("\n---Closing---\n")
            sys.exit()
            
    # Parcours de la liste des json à vérifier
    for json_i in jsonNames_list :

        # Création des nom de fichier 
        tested_filePath = Path(tested_folderPath).joinpath(json_i + '.json') #<<Mettre un assert là dessu ? (prévention d'un problème sur les caractères exotiques)
        schema_filePath = Path(schema_folderPath).joinpath(json_i + '_schema.json')
        
        # Check existance des fichiers   
        for file in [tested_filePath, schema_filePath] :#<<Utiliser un dic pr renvoyer un message d'erreur specifique test/schema
            if not Path(file).exists() :
                print(f"Verify the deduced file path: issue on {json_i} \n(expected {file} was not found).")
                print("\n---Closing---\n")
                sys.exit()
                
        # Lecture des fichiers
        with open(tested_filePath) as testedJson_file:
            tested_json_i = json.load(testedJson_file)
        with open(schema_filePath) as schemaJson_file:
            schema_json_i = json.load(schemaJson_file)

        # Test de validité du json vs son schéma
        jsonschema.validate(instance= tested_json_i, schema=schema_json_i) # If no exception is raised by validate(), the instance is valid.

        # Retour user pour l'item courant de la boucle
        print(f"The tested {json_i} json file is conform to its json-schema.")

        # Incrémentation de la liste des fichiers traités
        validated_json.append(json_i)

    # Retour user pr l'ensemble du process
    print(f"\n---Results---\n{len(validated_json)} json were validated against their schema")
    if len(validated_json)==len(jsonNames_list) :
        print("All json files required for PAS Modelling have been succefuly checked.") 
    print("\n---Closing---\n")

# CALL terminal
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process executable options.")
    parser.add_argument(
        '-stp', '--setTestedPath', type=str, help="To specify the path to the folder containing the set of json to test. (by default your current foder is use)"
    )

    parser.add_argument(
        '-ssp', '--setScemasPath', type=str, help="To specify the path to the folder containing the reference of json-schema. (by default in tools/json_cheker/json_schemas)"
    )
    args = parser.parse_args()
    main(args.setTestedPath, args.setScemasPath)