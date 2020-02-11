# Set demoCHR2018

## Etat
Ce set permet de générer un output, mais il n'est pas encore propre pr deux raisons.
**ToDo :** compléter le set de paramètres

## Purpose
Fournir un output représentatif de la stack actuelle (avec les défauts de l'import des CHR)

## Prb CHR
Les CHR sont issus des call à Bassens sur 2018.
Ont été écartés les CHR conduisant à un plantage (par exemple les CHR sans dock), mais il reste non conforme aux recommandations.
Le problème est que pr chaque escale 2 CHR ont été créées même si un seul à du sens. Pour chaque escale, un Loading ET un Unloading sont créés. On a donc beaucoup de CHR qui non pas de sens, avec :
- "category": "" ==> convertis en "category": "unknown"
- "amout":0

## Prb paramètres
Les paramètres ont été générés au plus vite pr ne pas provoquer de plantage (ex: Work en Sequential au lieu de Serie), un certain nombre de SC fictives ont été créées, mais ne couvre pas tous les cas. Le travail en cours de génération (automatique) d'un set de paramètres doit être continué.