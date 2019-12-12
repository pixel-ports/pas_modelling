import copy


class Step2:
    """ Affect a supplychain to each handling
    """

    def __init__(self, pas, supplychains):
        self.pas = pas
        self.supplychains = supplychains

    def run(self):
        for supplychain in self.supplychains:
            for step in supplychain["steps"]:
                step["full_id"] = "%s-%s" % (
                    supplychain["ID"],
                    step["ID"],
                )  # For later use in Step3
        for stopover in self.pas:
            for handling in stopover["handlings"]:
                assert (
                    handling["type"] == "cargo"
                ), "Handling types other than 'cargo' are not yet implemented"
                selected_supplychain, mapping_type = self.select_supplychain(handling)
                if selected_supplychain is None:
                    handling["supplychain"] = None
                else:
                    handling["supplychain_id"] = selected_supplychain["ID"]
                    handling["supplychain"]["mappingType"] = mapping_type
        return self.pas

    def get_default_supplychain(self):
        return (
            None
        )  # TODO Set default supplychain in the collection and define a way to select it. It will certainly be the ID of the supplychain defined in the RULE_MAPPER.

    def select_supplychain(self, handling):
        filtered_supplychains = [
            sc for sc in self.supplychains if is_matching(handling, sc)
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
    handling_segment_type = handling["content"]["segment_type"]
    handling_type = handling["content"]["type"]
    return handling_segment_type in supplychain["constraints"]["cargoes_types"][
        "segment"
    ] and (
        handling_type in supplychain["constraints"]["cargoes_types"]["type"]
        or supplychain["constraints"]["cargoes_types"]["type"] == "*"
    )
