 # Test données brutes IH



# Contexte

“nous souhaiterions tester le PAS modelling sur les données (historique d'un mois des données réelles de GPMB) remontées puis stockées sur PIXEL.”

# Source

curl -o data_IH_brutes.json -H "X-Auth-Token: b82e89e873834116fdd57cea3a0caebd676409d7" -H "Fiware-Service: PIXEL" -H "Fiware-ServicePath: /FRBOD" --insecure "https://dal.pixel-ports.eu/orion/v2/entities?q=departure_dock==2018-01-01T00:00:00.00Z..2018-12-31T23:59:59.59Z"



