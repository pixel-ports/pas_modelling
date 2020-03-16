#%%
variable = {"un dict"}
fstring = f"mon test et ma variable : {variable}"
module_name = "toto"
LOGS = {}

#%%%
toto = []
toto.append(["ceci"])
toto.append("test")
print(toto)

#%%

tmp = LOGS.get(module_name, [])
tmp.append("test")
print(tmp)

#%%

(LOGS.get(module_name, [])).append("test")
print(LOGS)
#%%
def LOGGER(conteneurDeLogs, prefix, message):
    return conteneurDeLogs.get(prefix, []).append("test")

print(LOGGER(LOGS, module_name, fstring))

print(LOGS)

# %%
