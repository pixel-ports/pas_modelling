import json
import argparse
import datetime

def main(input_filepath, output_filepath):
    with open(input_filepath) as json_file:
        data = json.load(json_file)

    output_data = [{
        "terminal": "default",
        "ships_list": []
    }]
    for call in data[0]["records"]:
        print(call)
        # direction = call["operation"]["value"]
        
        if ( call["%s_berth" % direction]["value"] != None and #devra passer en str(None) lorsque l input sera bien en string
            call["arrival_dock"]["value"] != str(None) and
            direction != None and
            call["%s_cargo_type" % direction]["value"] != None and
            call["%s_tonnage" % direction]["value"] != None and
            call["%s_tonnage" % direction]["value"] !=0
        ) :

        #     if call["IMO"]["value"] not in [ship["ID"] for ship in output_data[0]["ships_list"]]:
        #         output_data[0]["ships_list"].append({
        #             "ID": call["IMO"]["value"],
        #             "label": call["name"]["value"],  # Is that unique per ship ?
        #             "stopovers_list": []
        #         })
        #     ship = next(ship for ship in output_data[0]["ships_list"] if ship["ID"]==call["IMO"]["value"])

        #     if call["journeyid"]["value"] not in [stopover["ID"] for stopover in ship["stopovers_list"]]:
        #         ship["stopovers_list"].append({
        #             "ID": call["journeyid"]["value"],
        #             "handlings_list": []
        #         })
        #     stopover = next(stopover for stopover in ship["stopovers_list"] if stopover["ID"]==call["journeyid"]["value"])

        #     stopover["handlings_list"].append({
        #                         "nature": "cargo",
        #                         "dangerous": call["%s_dangerous" % direction]["value"],
        #                         "agent": call["%s_agent" % direction]["value"],
        #                         "dock": {
        #                             "ID": call["%s_berth" % direction]["value"],
        #                             "ETA": datetime.datetime.strptime(call["arrival_dock"]["value"], "%Y-%m-%dT%H:%M:%S.%fZ").isoformat(),
        #                             "ETD": datetime.datetime.strptime(call["departure_dock"]["value"], "%Y-%m-%dT%H:%M:%S.%fZ").isoformat()
        #                         },
        #                         "contents": {
        #                             "segment": call["%s_cargo_fiscal_type" % direction]["value"],
        #                             "direction": direction,
        #                             "category": call["%s_cargo_type" % direction]["value"],
        #                             "amount": call["%s_tonnage" % direction]["value"]
        #                         }
        #                     })


    with open(output_filepath, 'w') as outfile:
        outfile.write(json.dumps(output_data, indent=4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process executable options.")
    parser.add_argument(
        "--input_filepath", type=str, help="Filepath of the json to read"
    )
    parser.add_argument(
        "--output_filepath", type=str, help="Filepath of the json to read"
    )
    args = parser.parse_args()
    main(args.input_filepath, args.output_filepath)