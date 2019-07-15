from typing import Dict, List, Any

class Activity:

    def __init__(self, data):
        self.pair: Dict[str, Any] = data["pair"]
        self.logs: Dict[str, Any] = data["logs"]

    @staticmethod
    def produce_one(activity_dict: Dict[str, Any]) -> "Activity":
        return Activity(activity_dict)

    @staticmethod
    def produce_many(activity_dict_list : List[Dict[str, Any]]) -> List["Activity"]:
        return [Activity.produce_one(activity_dict) for activity_dict in activity_dict_list]
