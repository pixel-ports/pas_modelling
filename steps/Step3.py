import copy
import numpy as np
import datetime


class Step3:
    def __init__(self, pas, supplychains, resources):
        self.pas = pas
        self.supplychains = supplychains
        self.resources = resources
        self.uses = []

    def __get_sorted_handlings(
        self
    ):  # TODO : This function is also defined in Step2, so we should merge it
        """
        Precondition : handlings have been sorted in Step1 earlier
        """
        handlings = [
            handling
            for terminal in self.pas
            for ship in terminal["ships_list"]
            for stopover in ship["stopovers_list"]
            for handling in stopover["handlings_list"]
        ]
        handlings.sort(key=lambda handling: handling["ID"])
        return handlings

    def __find_minimal_starting_datetime(self, step, docking_datetime, ids_processed, activities):
        if step["scheduling"]["start"]["nature"] == "delay":
            starting_datetime = (
                docking_datetime
                + datetime.timedelta(
                    0, 60 * step["scheduling"]["start"]["value"]
                )
            )
            step_processed = True
        else:
            filtered_ids = [
                id
                for id in ids_processed
                if id in step["scheduling"]["start"]["value"]
            ]
            filtered_activities = [
                activity
                for activity in activities
                if activity["ID"] in filtered_ids
            ]
            if len(filtered_activities) > 0:
                if step["scheduling"]["start"]["nature"] == "with_any":
                    starting_datetime = min(
                        [
                            datetime.datetime.fromisoformat(activity["timespan_scheduled"]["start"])
                            for activity in filtered_activities
                        ]
                    )  # TODO : does min works with datetime ?
                elif (
                    step["scheduling"]["start"]["nature"] == "after_any"
                ):
                    starting_datetime = min(
                        [
                            datetime.datetime.fromisoformat(activity["timespan_scheduled"]["end"])
                            for activity in filtered_activities
                        ]
                    )  # TODO : does min works with datetime ?
                elif (
                    step["scheduling"]["start"]["nature"] == "with_all"
                ):
                    starting_datetime = max(
                        [
                            datetime.datetime.fromisoformat(activity["timespan_scheduled"]["start"])
                            for activity in filtered_activities
                        ]
                    )  # TODO : does min works with datetime ?
                elif (
                    step["scheduling"]["start"]["nature"] == "after_all"
                ):
                    starting_datetime = max(
                        [
                            datetime.datetime.fromisoformat(activity["timespan_scheduled"]["end"])
                            for activity in filtered_activities
                        ]
                    )  # TODO : does min works with datetime ?
                else:
                    raise ValueError(
                        'step["scheduling"]["start"]["nature"] contains an unknown value : %s'
                        % step["scheduling"]["start"]["nature"]
                    )
                step_processed = True  # TODO : Add this as an activity instead ?
            else:
                step_processed = False
        return starting_datetime if step_processed else None

    def __find_minimal_ending_datetime(self, handling, step, starting_datetime, ids_processed, activities):
        filtered_machines = self.__get_machines_for_step(step)
        if step["scheduling"]["duration"]["nature"] == "delay":
            assert (
                step["scheduling"]["duration"]["value"][1]
                == "min"
            ), "Not yet implemented : Duration unit is not min"
            ending_datetime = (
                starting_datetime
                + datetime.timedelta(
                    0,
                    step["scheduling"]["duration"]["value"][0]
                    * 60,
                )  # TODO : Check that we can do that with datetimes
            )
        elif step["scheduling"]["duration"]["nature"] in [
            "cargo_%",
            "cargo_tons",
        ]:
            # TODO : write here
            assert (
                len(
                    set(
                        [
                            machine["throughput"]["Unit"]
                            for machine in filtered_machines
                        ]
                    )
                )
                == 1
            ), "Cannot use parallel/serie machines if they don't have the same throughput Unit."
            assert (
                filtered_machines[0]["throughput"]["Unit"]
                == "t/h"
            ), (
                "Machine throughput should be expressed per hour, but is %s"
                % next(filtered_machines)["throughput"]["Unit"]
            )
            if step["work"]["nature"] == "parallel":
                throughput = sum(
                    [
                        machine["throughput"]["Value"]
                        for machine in filtered_machines
                    ]
                )
            elif step["work"]["nature"] == "serie":
                throughput = min(
                    [
                        machine["throughput"]["Value"]
                        for machine in filtered_machines
                    ]
                )
            if (
                step["scheduling"]["duration"]["nature"]
                == "cargo_%"
            ):
                duration_use_hours = (
                    handling["contents"]["amount"]
                    * step["scheduling"]["duration"]["value"]
                    / 100  # Suppose that duration value is in percents
                    * 1.0
                    / throughput
                )  # t/hour
            else:  # cargo_tons
                duration_use_hours = (
                    min(
                        [
                            handling["content"]["amount"],
                            step["scheduling"]["duration"][
                                "value"
                            ],
                        ]
                    )
                    * 1.0
                    / throughput
                )  # t/hour
            ending_datetime = (
                starting_datetime
                + datetime.timedelta(
                    0, duration_use_hours * 60 * 60
                )
            )
        else:
            filtered_ids = [
                id
                for id in ids_processed
                if id in step["scheduling"]["duration"]["value"]
            ]
            filtered_activities = [
                activity
                for activity in activities
                if activity["ID"] in filtered_ids
            ]
            if (
                step["scheduling"]["duration"]["nature"]
                == "before"
            ):
                ending_datetime = min(
                    [
                        datetime.datetime.fromisoformat(activity["timespan_scheduled"]["start"])
                        for activity in filtered_activities
                    ]
                )
            elif (
                step["scheduling"]["duration"]["nature"]
                == "after_any"
            ):
                ending_datetime = min(
                    [
                        datetime.datetime.fromisoformat(activity["timespan_scheduled"]["end"])
                        for activity in filtered_activities
                    ]
                )
            elif (
                step["scheduling"]["duration"]["nature"]
                == "after_all"
            ):
                ending_datetime = max(
                    [
                        datetime.datetime.fromisoformat(activity["timespan_scheduled"]["end"])
                        for activity in filtered_activities
                    ]
                )
            else:
                raise ValueError(
                    'step["scheduling"]["duration"]["nature"] contains an unknown value : %s'
                    % step["scheduling"]["duration"]["nature"]
                )
        return ending_datetime

    def __get_machines_for_step(self, step):
        return [
            machine
            for machine in self.resources["machines"]
            if machine["ID"] in step["work"]["machines"]
        ]

    def run(self):
        activity_next_free_id = 0
        for stopover in self.pas:
            for handling in self.__get_sorted_handlings():
                docking_datetime = datetime.datetime.fromisoformat(
                    handling["dock"]["ETA"]
                )
                supplychain = next(
                    sc
                    for sc in self.supplychains
                    if sc["ID"] == handling["supply_chain_ID"]
                )  # Raise a StopIteration if no matching element is found : https://stackoverflow.com/a/2364277/6463920
                if supplychain is not None:
                    steps = supplychain["steps_list"]
                    activities = []
                    ids_to_process = [step["ID"] for step in steps]
                    ids_processed = []
                    while len(ids_to_process) > 0:
                        for id in ids_to_process:
                            step = next(step for step in steps if step["ID"] == id)
                            filtered_machines = self.__get_machines_for_step(step)
                            starting_datetime = self.__find_minimal_starting_datetime(step, docking_datetime, ids_processed, activities)
                            if starting_datetime is not None:
                                ending_datetime = self.__find_minimal_ending_datetime(handling, step, starting_datetime, ids_processed, activities)         
                                ids_to_process.remove(id)
                                ids_processed.append(id)
                                starting_datetime, ending_datetime = self.get_next_available_TS_multiple_machines(
                                    filtered_machines,
                                    starting_datetime,
                                    ending_datetime
                                )
                                activity = {
                                    "ID": activity_next_free_id,
                                    "step_ID": step["ID"],
                                    "timespan_scheduled": {
                                        "start": starting_datetime.isoformat(),
                                        "end": ending_datetime.isoformat(),
                                        "duration": (ending_datetime - starting_datetime).total_seconds()/60
                                    },
                                    "ressources_accounts_list": [{
                                        "ressource_ID": machine["ID"]
                                    } for machine in filtered_machines]
                                }
                                activity_next_free_id += 1
                                activities.append(activity)

                                for machine in filtered_machines:  # Usefull to check for machine availability
                                    self.uses.append(
                                        {
                                            "start": starting_datetime,
                                            "end": ending_datetime,
                                            "machine": copy.deepcopy(machine)
                                        }
                                    )
                handling["activities_list"] = activities
        return self.pas

    def get_use(self, handlingId: int, supplychainId: int, operationId: int):
        uses = [
            use
            for use in self.uses
            if use["handling"]["id"] == handlingId
            and use["activity"]["id"] == "%s-%s" % (supplychainId, operationId)
        ]
        assert len(uses) == 1, "Undefined uses or multiples use of the same id"
        return uses[0]

    def get_overlapping_TS(
        self, machine: dict, start: datetime, end: datetime
    ) -> (datetime, datetime):
        machine_uses = [
            use for use in self.uses if machine["id"] == use["machine"]["id"]
        ]
        for use in machine_uses:
            if (
                use["start"] < start < use["end"]
                or use["start"] < end < use["end"]
                or (start < use["start"] and use["end"] < end)
            ):
                return use["start"], use["end"]
        return None, None

    def is_available(self, machine: dict, start: datetime, end: datetime) -> bool:
        return self.get_overlapping_TS(machine, start, end) == (None, None)

    def get_next_available_TS(
        self, machine: dict, start: datetime, end: datetime
    ) -> (datetime, datetime):
        """ Return the next available timespan for one machine
        """
        while True:
            if self.is_available(machine, start, end):
                return start, end
            else:
                _, o_end = self.get_overlapping_TS(machine, start, end)
                delta: int = end - start
                start: int = o_end
                end: int = start + delta

    def get_next_available_TS_multiple_machines(
        self, machines: list, start: datetime, end: datetime
    ) -> (datetime, datetime):
        """ Return the next available common timespan for multiple machines. It does not matter if the machines are running in parrallel or serie because we book the global timespan for all the machines.
        """  # TODO : Manage the case when no combination can be found (and prevent an infinite while loop)
        duration = end - start
        while True:
            starts = [self.get_next_available_TS(machine, start, end)[0] for machine in machines]
            if len(set(starts)) == 1:
                start = starts[0]
                return start, start + duration
            else:
                start = max(starts)
