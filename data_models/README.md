# <<test 3

# DATA-MODELS README

This REadMe provide an overview of the PAS Modelling’s data-models. Detailed specification and utilities for json validity check are provide through the X_schema.json file that are provided for each data-model.

# Overview

To run, PAS builder require one *input* document and several *parameters* document. The main difference is that  intrinsically *input* are more dynamic, whereas *parameters* are more static. That is to say, generally the input is different for every run of the model, whereas parameters are keep identical for numerous run. In the PAS builder context :

- the input contains the data about "what have to be handled" (e.g. list of ships' cargoes handling requested)
- the parameters contain the data about "what are the resources to do it" (e.g. description of port's assets such machines and process such rules for priority attribution)
- the output is an exhaustive list of the resulting list of timestamped activities paired with the corresponding cargo and resources 

# Input

The model’s input is the *Handling Requests*. This corresponds to a list of boats loading or unloading during a period of time. For each one, several information should be provided, with the fallowing structure: 

**Key points:**

- For convenience the json type is an array, but the *handling* order is not significant.
	- For a ship’s stopover corresponding to only a cargo loading or unloading, there will be only one *handling*. If the ship is both unloaded and then loaded (possibly at two distinct dock), then there will be two *handling*. For ship with multi-compartment containing distinct cargo that will be load or unload, several handling can be use.
- The minimal required information are : handling’s type, dock ID and ETA, content’s direction, type and amount.
	- Providing other listed information will enhance the PAS modelling's output quality and usefulness.
- The content bloc could evolve to reflect different data needs for cargo, passengers and containers modelling.
	- Currently, only handlings having a type “cargo” are suitable for PAS Modelling.

# Parameters

The parameters of the model are information necessary for its execution, but having an inherently more static character than the input.

Collections refer to entities that have the lowest level of abstraction in port activity modelling context. That is to say, entities that can be approximated as physical objects.
Collections refer to entities that have the highest level of abstraction in port activity modelling context. That is to say, entities that can be approximated as process habits.

- Ressources
	- Ajouter un level pr terminal ?
- Areas
	- examples":["docks", "silo", "warehouses", "office", "gates", "other"]
- Cargoes
- Machines
- SupplyChains
	- Définir les step
	- Présenter l’affectation de n machine
	- Expliquer prallalèle ou série
- Rules
	- Priorities
	- Assignments
	- Validities

# Output

