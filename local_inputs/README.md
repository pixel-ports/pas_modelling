On a deux ensembles pr tester en local.

# Inputs en fichiers séparées
Ce type d'input ignore le PAS_instance (qui est l'input reçu des OT lors de l'appel du PAS modelling). Tous les fichiers sont séparés.
Pour les cargo handling requests, c'est un format relativement à jour vis à vis de ce qui est remonté de GPMB (par Orange) dans l'IH.
Pour les paramètres du port, les data modèles sont au format Master v3 à quelques détails près (modifications demandées par ProD pour la GUI).
## Pipeline
## VSCode launcher

# Inputs unifiés dans le PAS instance
Ce type d'input en local reste basé sur le PAS_instance, mais ce dernier contient directement tous les inputs (handlings + port's parameters) sans renvoyer à l'IH. 