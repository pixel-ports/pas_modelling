import json
import jsonschema
import jsonref

# PATHS ET FICHIERS ------------------------
#path = "./tools/json_checker/json_schemas/test/" #Run terminal (cwd est la racine)
path = "./" #Run iPython (cwd est le dossier de ce .py)

tested_filePath = path + "handling.json"
schema_filePath = path + "CHR.schema.json"
#schema_filePath = path + "handling.schema"

# USER PRINT ------------------------
#print(tested_filePath, schema_filePath)


# PROCESSING ------------------------
# Chargement des fichiers
with open(tested_filePath) as testedJson_file:
    tested_json_i = json.load(testedJson_file)
with open(schema_filePath) as schemaJson_file:
    schema_json_i = json.load(schemaJson_file)
    # Tentative de test sur un sous composant
    #sub_schema_json_i=jsonref.loads(schemaJson_file, "ref":{"$ref":"#/handling_item"})

handling_schema = schema_json_i["items"]["properties"]["ships_list"]["items"]["properties"]["stopovers_list"]["items"]["properties"]["handlings_list"]["items"]


print("\n\n\nRésultat : \n")
# Test de validité du json vs son schéma
jsonschema.validate(instance= tested_json_i, schema=handling_schema) # If no exception is raised by validate(), the instance is valid.



# Retour user pour l'item courant de la boucle
print(f"The tested {tested_filePath} json file is conform to its json-schema ({schema_filePath}).\n\n\n")