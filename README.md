# PIXEL Port Activity Scenario Modelling

## Data Models

For the ships:
```js
{
    "ship": {
        "shipId": 0,
        "arrivingTime": 1562924315,  // timestamp in seconds
        "berthAllocation": null
    },
    "cargo": {
        "category": "cereal",  // solidBulk, cereal, hydrocarbons
        "type": "slag",  // slag, cornBulk, butadiene
        "amount": 10,
        "availabilityTS": 3600  // in seconds 
    },
    "constraint": {
        "priority": 2,  // either set at cargo creation or with the rule-based method
        "departureTime": null,
        "weather": [],  // some conditions about the weather
        "operator": []
    },
    "logs": {
        "comments": [],
        "modifications": []
    }
}
```

For the Supply-Chains:
```js
{
    "identification":{
        "name": "firstSupplychain",
        "terminal": [],
        "operator": [],
        "suitableCargoType": ["slag"],
        "suitableAreas": [],
        "priority": null,
        "comments": []
    },
    "operationsSequence": [
        {
            "title": null,
            "startType": null,
            "distance": 0,
            "machinesID": [],
            "endType": null
        }
    ]
}
```