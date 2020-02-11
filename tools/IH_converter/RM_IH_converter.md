# IH Converter

## Purpose
Convertir les données de l'IH en un input CHR valide.

## Use Example

## Current state
Laissé en plan, en attente d'une stabilisation de l'IH (du fait des données aberrantes présentes)

### To Do
[] Reconstituer une arborescence valide, en particulier en créant uniquement des handlings valides (et non pas automatiquement des paires unload+load comme dans l'IH présentement)
[] N'enregistrer un handling que s'il respecte le json-schema (attention, on parle ici d'une sous-structure précisément pr un handling, pas pour l'input CHR entier) ==> subdiviser le json-schema de CHR et l'appeler pr le test
[] A la cloture, vérifier que l'input global CHR est valide (vérification d'ensemble)

### Change Log

