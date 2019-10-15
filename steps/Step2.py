import copy


class Step2:
    def __init__(self, pas_input, supplychains):
        self.pas_input = pas_input
        self.supplychains = supplychains

    def run(self):
        for id, supplychain in self.supplychains.items():
            supplychain["id"] = id
            for id_op, operation in supplychain["OPERATIONS_SEQUENCE"].items():
                operation["id"] = "%s-%s" % (id, id_op)  # For later use in Step3
        for ship in self.pas_input:
            for handling in ship["HANDLINGS"]:
                if handling["CARGO"] is None:
                    handling["supplychain"] = None
                else:
                    selected_supplychain, mapping_type = self.select_supplychain(
                        handling
                    )
                    if selected_supplychain is None:
                        handling["supplychain"] = None
                    else:
                        handling["supplychain"] = copy.deepcopy(selected_supplychain)
                        handling["supplychain"]["mappingType"] = mapping_type
        return self.pas_input

    def get_default_supplychain(self):
        return (
            None
        )  # TODO Set default supplychain in the collection and define a way to select it. It will certainly be the ID of the supplychain defined in the RULE_MAPPER.

    def select_supplychain(self, handling):
        for id, sc in self.supplychains.items():
            sc["id"] = id
        filtered_supplychains = [
            sc for _, sc in self.supplychains.items() if is_matching(handling, sc)
        ]

        selected_supplychain = None  #  Default if no supplychain is matched
        mapping_type: str = "default"

        if len(filtered_supplychains) == 0:
            selected_supplychain = self.get_default_supplychain()
            mapping_type = "default"
        elif len(filtered_supplychains) == 1:
            selected_supplychain = filtered_supplychains[0]
            mapping_type = "direct"

        # TODO Select prioritized supplychain when prioritize rule will be defined
        return selected_supplychain, mapping_type


def is_matching(handling, supplychain):
    assert (
        len(handling["CARGO"]["Type"].keys()) == 1
    ), "Handling cargo has more than one type"
    handling_type = list(handling["CARGO"]["Type"].keys())[0]
    return (
        handling_type
        in supplychain["IDENTIFICATION"]["HS?(SUITABILITY)"]["Cargo_Type"].keys()
        and handling["CARGO"]["Type"][handling_type]
        in supplychain["IDENTIFICATION"]["HS?(SUITABILITY)"]["Cargo_Type"][
            handling_type
        ]
    )
