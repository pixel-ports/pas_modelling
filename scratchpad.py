#%% 
import json
with open("./settings.json") as file :
    SETTINGS = json.load(file)

pipeline_name = "GPMB_demo"	
modules_sequence = SETTINGS["pipelines"][pipeline_name]

SETTINGS

relevant_modul={}
#%%
for (key, content) in SETTINGS["modules_settings"].items():
    if key in modules_sequence:
        relevant_modul.update({key: content})
        


#%%
{
    {key: content} 
    for (key, content) in SETTINGS["modules_settings"].items() 
    if  key in modules_sequence
}


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
