# PAS modeling's data-model ReadMe

## Principe de fonctionnement du PAS builder (et des data-models associés)

À partir de la liste des enregistrements de manipulation de marchandise enregistrés, on établi :
- l'ordre de priorité des prises en charge des bateau
- la supply-chain correspondante
- le planning d'activité correspondant
Chaque étape va consister à ajouter au PAS.json des informations.

### Initializater
A partir des API disponibles, on construit une liste des Handling. 
NB : le call d'un bateau entrant dans le port chargé et repartant chargé va générer au moins deux demandes d'handlings. Le premier en déchargement, le second en chargement.

### Prioritizer
On associe à chaque Handling de la liste un ordre de priorité de traitement. Cet ordre n'est pas équivalent à l'ordre de traitement qui sera finalement calculé, mais est nécessaire pour établir ce planning.

### Mapper
On associe à chaque Handling de la liste la supply-chain qui sera utilisée.

### Scheduler
On projette la séquence d’handling sur l'axe du temps, de manière à obtenir un TS de début et de fin pour chaque opération élémentaire.

## Data-models

### PAS_[input, output]
Une arborescence dont la racine est une escale. Peut contenir n handling (correspondant à m chargements et p déchargements).
Le passage à travers le PAS Builder ajoute des clés, jusqu'à une granularité maximale de l'activité. C'est-à-dire la projection dans le temps (TS de début et de fin) des opérations.

### Collection_[Area, CargoType, Machine, SupplyChain]
Des collections de références "physiques" pour lesquelles le port a fournit une description selon le data-model associé.

### Rules_[Checker, Mapper, Prioritizer, Scheduler]
Des arrays de règles à utiliser pour 

## Todo
- Ajouter Rules_Scheduler.json, compléter les autres (cf Area, Checker...)
- Homogénéiser les noms de clés et ID variables
- Augmenter le nombre de faux enregistrements dans PAS_input
- Débuger :)
