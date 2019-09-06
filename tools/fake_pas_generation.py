import random
import time
import json

pas = {
    "metadata": {
        "pasID": "8b5e871e-8938-468d-ba5d-2ac48822cd25",
        "creationTS": 1566487577,
        "creatorID": "rquera",
        "status": None,
        "parents": {
            "cargoQueueID": None,
            "supplychainCollectionID": None,
            "activitiesQueueID": None,
            "machineCollectionID": None
        },
        "logs": {
            "comments": [],
            "modifications": []
        }
    },
    "timeseries": []
}

actualTs = int(time.time())

scs_number = 10
machines_number = 50
cargoes_number = 100

timeToMonitor = 60*60*24*3
minMachineDuration = 60*60
maxMachineDuration = 5*60*60
minGapBetweenTwoMachinesUses = 0
maxGapBetweenTwoMachinesUses = 2*60*60
scIds = ["sc_%d" % i for i in range(scs_number)]
operations_names = ["raise", "drop", "drive", "load", "unload", "filter"]
cargoesIds = ["cargo_%d" % i for i in range(cargoes_number)]
energyTypes = ["gazole", "diesel", "essence", "fuel"]  # https://www.total.fr/pro/carburants/carburants-marins

operation_number = 0
for machineId in ["machine_%02d" % i for i in range(machines_number)]:
    machine = {
        "machineId": machineId,
        "consumption": {
            "energyType": random.choice(energyTypes),
            "consumptionPerHour": random.randint(5, 25)
        },
        "uses": []
    }
    lastTs = actualTs
    useNumber = 0
    while lastTs < actualTs + timeToMonitor:
        gapInSeconds = random.randint(minGapBetweenTwoMachinesUses, maxGapBetweenTwoMachinesUses)
        startTs = lastTs + gapInSeconds
        duration = random.randint(minMachineDuration, maxMachineDuration)
        endTs = startTs + duration
        lastTs = endTs

        operationId = "op_%d" % operation_number
        operation_number += 1
        operationName = random.choice(operations_names)
        scId = random.choice(scIds)
        cargoId = random.choice(cargoesIds)

        use = {
            "startTs": startTs,
            "endTs": endTs,
            "duration": duration,
            "operationId": operationId,
            "operationName": operationName,
            "supplychainId": scId,
            "cargoId": cargoId
        }
        machine["uses"].append(use)
        useNumber += 1
    pas["timeseries"].append(machine)

with open('port_activity_scenario.json', 'w') as f:
    json.dump(pas, f, indent=4)





    


        



