#%% 
import json
HANDLINGS = {
	"input": [
        {
            "name": "Handlings",
            "endpoint": "./inputs/GPMB/IH_2018.json",
            "type": "Vessel_Calls",
        },
        {
            "name": "Asignations",
            "endpoint": "./inputs/GPMB/Assignations.json",
            "type": "Port_parameters",
        },
        {
            "name": "Supplychains",
            "endpoint": "./inputs/GPMB/Supplychains.json",
            "type": "Port_parameters",
        },
        {
            "name": "Resources",
            "endpoint": "./inputs/GPMB/Resources.json",
            "type": "Port_parameters",
        }
    ]
}

def get(request):
	loaded_json = None
	try:
		with open(request["endpoint"]) as file :
			loaded_json = json.load(file)
	except FileNotFoundError: 
		message = f"{request.get('name', 'undefined name')} loading issue: invalid source ({request.get('endpoint', 'undefined endpoint')})"
		
	except ValueError: 
		message = f"{request.get('name', 'undefined name')} loading issue: invalid file"
	else:
		message = f"{request.get('name', 'undefined name')} succefully loaded"
	
	return message, loaded_json

#%%
toto = { key:value for (key, value) in HANDLINGS["input"].items()  }
toto
#%%
#l'ordre de récupération des fichiers est fixé dans settings?
for request in HANDLINGS["input"]:
	request_status, request_object = get(request)
	item = request_object
	print(request_status)
	# try:
	#     get(request)
	# except:
	#     print("exception levée")#Si possible distinguer source injoigniable et objet invalide (la validité vs schéma est déplacée ds le module de conversion)
	# else:
	#     print("tout ok")
print("end")


# %%

# %%
