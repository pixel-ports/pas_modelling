#==============================
# LIBRAIRIES
import pandas as pd
import pprint as pp #Pr des "jolis" prints des dic pp.pprint(*_dic)
import json #Pr convertir les dic en json utiliser json.dump (sans S) et avoir un "joli" print : print(json.dumps(*_dic, sort_keys=True, indent=4))

# AFFICHAGE NOTEBOOK
from IPython.core.interactiveshell import InteractiveShell # Mettre en output toutes les sortie d'une cellule
InteractiveShell.ast_node_interactivity = "all" #"last_expr"


with open("./IH_data/IH_2018.json") as json_file:
    json_IH = json.load(json_file)


# %%
# INSTANCIATION

source_df = json_normalize(
    json_IH[0], #On filtre sur 0 car on a un seul terminal présent
    record_path=[
        "records", 
        "data", 
    ], 
    meta=[ 
    ],
    sep="__"
)

source_df.shape
source_df


# %%
a="[]"
a
#source_df["handlings_list"].str.find(a)

source_df.iloc[4,source_df["handlings_list"]]


# %%
source_df.loc[source_df["handlings_list"]=="\[\]",:]


# %%
# EMPTY, NAN et 0

# Recherche
np.where(source_df.applymap(lambda x: x == ''))

# Remplacement
#source_df.replace("",np.nan, inplace=True)

# %% [markdown]
# ## Préparation

# %%
# CHARGEMENT

with open("/media/DATA/CODE/1_PIXEL/1_PAS_MODELLING/inputs/demoCHR2018/CARGOES_HANDLING_REQUESTS.json") as json_file:
    chr_json = json.load(json_file)


# %%
# INSTANCIATION

chr_df = json_normalize(
    chr_json[0], #On filtre sur 0 car on a un seul terminal présent
    record_path=[
        "ships_list", 
        "stopovers_list", 
        "handlings_list"
    ], 
    meta=[
        ["ships_list", "ID"],
        ["ships_list",'label'],
        ["ships_list", "stopovers_list", "ID"],    
    ],
    sep="__"
)

chr_df.shape
chr_df.head()


# %%
# RENOMMAGE COLONNES

chr_df.columns
chr_df.rename(
    columns={
        "dock__ID": "dock_ID", 
        "dock__ETA": "dock_ETA", 
        "dock__ETD": "dock_ETD",
        "contents__direction": "direction",
        "contents__category": "category",
        "contents__amount": "amount",
        "ships_list__ID": "ship_ID",
        "ships_list__label": "ship_label",
        "ships_list__stopovers_list__ID": "stopover_ID",
    },
    errors="raise",
    inplace= True
)


# %%
# EMPTY, NAN et 0

# Recherche
np.where(chr_df.applymap(lambda x: x == ''))

# Remplacement
#chr_df.replace("",np.nan, inplace=True)

# %% [markdown]
# Attention, ici les category = unknown sont des empty qui ont été remplacé. Cf le fait d'avoir des amount à 0

# %%
# Vérification de la bijection parfaite

(chr_df.loc[chr_df["category"] == "unknown", :] != chr_df.loc[chr_df["amount"] == 0, :]).sum()


# %%
chr_df.drop(
    chr_df.loc[chr_df["category"] == "unknown", :].index,
    inplace= True
)


# %%
# CONVERTION DE TYPE

#chr_df.astype({"data.loading_berth":'int32'})


# %%
# Nb d'enregistrement valide

chr_df.shape

# %% [markdown]
# # Dictionnaire des info pertinentes
# %% [markdown]
# PRB : dans cet input, il n'y a pas les segments. Ce qui va être problématique pr ramener les nCCat ==> 1CSeg --> 1SC

# %%
ct_groupe = pd.DataFrame(
    cargo_type.groupby("Type")["Groupe"].agg(lambda x:x.value_counts().index[0]) #On prend uniquement la valeur la plus fréquence (possible égalité)
)

#Alternative, utiliser fonction custom à appliquer :
  
def most_frequent(List): 
    occurence_count = Counter(List) 
    return occurence_count.most_common(1)[0][0] 
    
List = [2, 1, 2, 2, 1, 3] 
print(most_frequent(List)) 
# %%
ct_groupe.insert(1, "Dock", 
                 cargo_type.groupby("Type")["Dock"].apply(lambda x: pd.unique(x).tolist())) #On passe en valeur la liste de tous les docks ayant correspondus

# %% [markdown]
# # RESSOURCE

# %%
#load json object
with open('./RESSOURCES_demo.json') as json_file:
    ressources = json.load(json_file)

ressources = json_normalize(ressources['machines'])


ressources.head()

# %% [markdown]
# # OUTPUT

# %%
#load json object
with open('./Service Output Extended.json') as json_file:
    output = json.load(json_file)

output = json_normalize(output)


output.head()

