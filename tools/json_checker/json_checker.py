"""
=====================================================================
# README

## Current state
v0.2.1

## Purpose
This tool check if a given folder containing identified json are valid against their known json-schema.

## To do
Use a conf file instead of hard coded names & paths

## Use example: 
NB : si lancé depuis 1_PAS_MODELLING/tools/json_checker avec rules et ressources desactivés:
python3 json_checker.py \
    --tested_folderPath="../../inputs/simple_examples/" \
    --schema_folderPath="./json_schemas/"

==> 
---Processing---
The tested CARGOES_HANDLING_REQUESTS json file is conform to its json-schema.
The tested SUPPLYCHAINS json file is conform to its json-schema.
---Results---
2 json were validated against their schema
All json files required for PAS Modelling have been succefuly checked.
---Closing---
=====================================================================
"""


# LIBRAIRIES
import argparse
import json
import jsonschema
import os
import sys

# PRESET JSON NAME
jsonNames_list = [
    "CARGOES_HANDLING_REQUESTS",
 #   "RULES",
    "SUPPLYCHAINS",
#    "RESOURCES"
]

# MAIN
def main(tested_folderPath, schema_folderPath):
    # Check existance des dossiers
    cwd = os.getcwd()
    validated_json = []
    
    print("\n---Processing---\n")
    for folder in [tested_folderPath, schema_folderPath] :
        if not os.path.exists(folder) :
            print(f"Verify the given folder path: {folder} was not found. \nNote that you are currently in {cwd}")
            print("\n---Closing---\n")
            sys.exit()
            
    # Parcours de la liste des json à vérifier
    for json_i in jsonNames_list :

        # Création des nom de fichier 
        tested_filePath = os.path.join(tested_folderPath, json_i + ".json") #<<Mettre un assert là dessu ? (prévention d'un problème sur les caractères exotiques)
        schema_filePath = os.path.join(schema_folderPath, json_i + "_schema.json")
        
        # Check existance des fichiers   
        for file in [tested_filePath, schema_filePath] :#<<Utiliser un dic pr renvoyer un message d'erreur specifique test/schema
            if not os.path.exists(file) :
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
        "--tested_folderPath", type=str, help="Folder path to the json to test"
    )
    parser.add_argument(
        "--schema_folderPath", type=str, help="Folder path of the json-schema"
    )
    args = parser.parse_args()
    main(args.tested_folderPath, args.schema_folderPath)