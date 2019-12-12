import copy
import numpy as np
import datetime


class Step3:
    def __init__(self, pas, supplychains, machines):
        self.pas = pas
        self.supplychains = supplychains
        self.machines = machines
        self.uses = []

    def run(self):
        for id, machine in self.machines.items():
            machine["id"] = id

        for stopover in self.pas:
            for handling in stopover["handlings"]:
                docking_datetime = datetime.datetime.fromisoformat(
                    handling["dock"]["ETA"]
                )
                supplychain = next(
                    sc
                    for sc in self.supplychains
                    if sc["ID"] == handling["supplychain_id"]
                )  # Raise a StopIteration if no matching element is found : https://stackoverflow.com/a/2364277/6463920
                if supplychain is not None:
                    steps = supplychain["steps"]
                    activities = []
                    ids_to_process = [step["ID"] for step in steps]
                    ids_processed = []
                    while len(ids_to_process) > 0:
                        for id in ids_to_process:
                            step = next(step for step in steps if step["ID"] == id)
                            step_processed = False

                            if step["scheduling"]["start"]["type"] == "delay":
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

                                if step["scheduling"]["start"]["type"] == "with_any":
                                    starting_datetime = min(
                                        [
                                            activity["timespan_scheduled"]["start"]
                                            for activity in filtered_activities
                                        ]
                                    )  # TODO : does min works with datetime ?
                                elif step["scheduling"]["start"]["type"] == "after_any":
                                    starting_datetime = min(
                                        [
                                            activity["timespan_scheduled"]["end"]
                                            for activity in filtered_activities
                                        ]
                                    )  # TODO : does min works with datetime ?
                                elif step["scheduling"]["start"]["type"] == "with_all":
                                    starting_datetime = max(
                                        [
                                            activity["timespan_scheduled"]["start"]
                                            for activity in filtered_activities
                                        ]
                                    )  # TODO : does min works with datetime ?
                                elif step["scheduling"]["start"]["type"] == "after_all":
                                    starting_datetime = max(
                                        [
                                            activity["timespan_scheduled"]["end"]
                                            for activity in filtered_activities
                                        ]
                                    )  # TODO : does min works with datetime ?
                                else:
                                    raise ValueError(
                                        'step["scheduling"]["start"]["type"] contains an unknown value : %s'
                                        % step["scheduling"]["start"]["type"]
                                    )

                                step_processed = (
                                    True
                                )  # TODO : Add this as an activity instead ?

                            if step_processed:
                                filtered_machines = [
                                    machine
                                    for machine in self.machines
                                    in machine["ID"]
                                    in step["scheduling"]["work"]["machines"]
                                ]
                                if step["scheduling"]["duration"]["type"] == "delay":
                                    assert (
                                        step["scheduling"]["duration"]["value"][1]
                                        == "min"
                                    ), "Not yet implemented : Duration unit is not min"
                                    ending_datetime = (
                                        starting_datetime
                                        + datetime.timedelta(0, step["scheduling"]["duration"]["value"][0]
                                        * 60)  # TODO : Check that we can do that with datetimes
                                    )
                                elif (
                                    step["scheduling"]["duration"]["type"]
                                    == "cargo_amount"
                                ):
                                    assert (
                                        step["scheduling"]["duration"]["value"][1]
                                        == "%"
                                    )
                                    # TODO : write here
                                    assert (
                                        len(
                                            set(
                                                [
                                                    machines["throughput"]["Unit"]
                                                    for machine in filtered_machines
                                                ]
                                            )
                                        )
                                        == 1
                                    ), "Cannot use parallel/serie machines if they don't have the same throughput Unit."
                                    if step["work"]["type"] == "parallel":
                                        throughput = sum(
                                            [
                                                machine["throughput"]["Value"]
                                                for machine in filtered_machines
                                            ]
                                        )
                                    elif step["work"]["type"] == "serie":
                                        throughput = min(
                                            [
                                                machine["throughput"]["Value"]
                                                for machine in filtered_machines
                                            ]
                                        )
                                    duration_use_minutes = (
                                        handling["content"]["amount"]
                                        * step["scheduling"]["duration"]["value"][0]
                                        / 100  # Suppose that duration value is in percents
                                        * 1.0
                                        / throughput
                                    )  # t/minutes  # TODO : To check that it is the correct unit
                                    ending_datetime = (
                                        starting_datetime + datetime.timedelta(0, duration_use_minutes * 60)
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
                                        step["scheduling"]["duration"]["type"]
                                        == "before"
                                    ):
                                        ending_datetime = min(
                                            [
                                                activity["timespan_scheduled"]["start"]
                                                for activity in filtered_activities
                                            ]
                                        )
                                    elif (
                                        step["scheduling"]["duration"]["type"]
                                        == "after_any"
                                    ):
                                        ending_datetime = min(
                                            [
                                                activity["timespan_scheduled"]["end"]
                                                for activity in filtered_activities
                                            ]
                                        )
                                    elif (
                                        step["scheduling"]["duration"]["type"]
                                        == "after_all"
                                    ):
                                        ending_datetime = max(
                                            [
                                                activity["timespan_scheduled"]["end"]
                                                for activity in filtered_activities
                                            ]
                                        )

                                ids_to_process.remove(id)
                                ids_processed.append(id)
                                startingTS, endingTS = self.get_next_available_TS(
                                    machine, starting_datetime, ending_datetime
                                )
                                activity = copy.deepcopy(step)
                                activity["timespan_scheduled"] = {}
                                activity["timespan_scheduled"][
                                    "start"
                                ] = starting_datetime
                                activity["timespan_scheduled"]["end"] = ending_datetime
                                activity["duration"] = (
                                    ending_datetime - starting_datetime
                                )

                                for (
                                    machine
                                ) in (
                                    filtered_machines
                                ):  # TODO : IDK if it is still useful. It is but we could replace it by a on-the-fly uses retrieval
                                    self.uses.append(
                                        {
                                            "start": starting_datetime,
                                            "end": ending_datetime,
                                            "machine": copy.deepcopy(machine),
                                            "handling": copy.deepcopy(handling),
                                            "supplychain": copy.deepcopy(supplychain),
                                            "activity": copy.deepcopy(activity),
                                        }
                                    )
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

    def get_overlapping_TS(self, machine: dict, start: datetime, end: datetime) -> (datetime, datetime):
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

    def get_next_available_TS(self, machine: dict, start: datetime, end: datetime) -> (datetime, datetime):
        while True:
            if self.is_available(machine, start, end):
                return start, end
            else:
                _, o_end = self.get_overlapping_TS(machine, start, end)
                delta: int = end - start
                start: int = o_end
                end: int = start + delta
