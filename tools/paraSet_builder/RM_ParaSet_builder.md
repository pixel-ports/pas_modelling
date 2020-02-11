# Parameters Set Builder

## Purpose
A partir des données de transit de bateau d'un port, générer un set de paramètres pour le PAS modelling. Non pas un set final, mais une première trame.

### Principe
Basé sur le cas des données de l'IH de GPMB:
- prendre les infos exploitable
- sortir pr chaque categorie de cargaison :
	- le segment
	- la liste des docks observés
- ajouter les info nécessaire pour générer Rules (on présupose une SC par tuple (direction, segment))

## Use Example

## Current state
Embryonnaire : simplement la restructuration des infos sous un df pertinent.

### To Do
[] Générer les différents json de paramètres.
[] N'enregistrer un handling que s'il respecte le json-schema (attention, on parle ici d'une sous-structure précisément pr un handling, pas pour l'input CHR entier) ==> subdiviser le json-schema de CHR et l'appeler pr le test
[] A la cloture, vérifier que l'input est valide vis à vis des schémas :
	- par item
	- au global

### Change Log

