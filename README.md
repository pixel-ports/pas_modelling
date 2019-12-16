# PIXEL Port Activity Scenario Modelling
# Version: v1.0 - Ljubljana

This repository implements the PAS modelling presented in the MTC paper : https://www.dropbox.com/s/6z2e854bxz9jtur/MTC2019_SIMON_LACALLE.pdf?dl=0.

![Cross Modelling](./tools/resources/cross_modelling.png "PIXEL cross modelling")

## Run the model

You'll need docker to run the PAS docker image : https://docs.docker.com/install/linux/docker-ce/ubuntu/

One run of the PAS start the container, load input files specified in the `.env` file, outputs results files to the `outputs` folder and exits.  
It runs with the following commands :

```bash
docker build -t pas .
sudo rm -rf outputs && mkdir outputs
docker run --env-file .env -v $(pwd):/pas pas python3 main.py --steps 1 2 3 4
```

## Manage data coming from the Information Hub (IH)

The exprimed context, in french : "Nous souhaiterions tester le PAS modelling sur les données (historique d'un mois des données réelles de GPMB) remontées puis stockées sur PIXEL."

In order to retrieve data from GPMB API :

```bash
curl -o data_IH_brutes.json -H "X-Auth-Token: b82e89e873834116fdd57cea3a0caebd676409d7" -H "Fiware-Service: PIXEL" -H "Fiware-ServicePath: /FRBOD" --insecure "https://dal.pixel-ports.eu/orion/v2/entities?q=departure_dock==2018-01-01T00:00:00.00Z..2018-12-31T23:59:59.59Z"
```

And then, to convert the downloaded data into input_data for the PAS modelling :
```bash
docker build -t pas .
sudo rm -rf outputs && mkdir outputs  # Even if we put it in the `outputs` folder, we are generating the `input` for the PAS_modelling
docker run -v $(pwd):/pas pas python3 ./tools/gpmb_ships_call_list_converter/converter.py --input_filepath tools/gpmb_ships_call_list_converter/data_IH_brutes.json --output_filepath ./outputs/INPUT_GPMB_generated_from_ships_call_list.json
```

<!--  
## Statistics for WP8 Product Quality Model - This has to be adapted to the docker usage

```bash
# Reinit output
rm -rf outputs/ && mkdir outputs

# Set steps to monitor
export PAS_STEPS="4"  # "1 2 3" for T4.1 or "4" for T4.2

# Monitoring RAM
pipenv run valgrind --tool=massif --time-unit=ms python main.py --steps $PAS_STEPS
pipenv run python monitor/massif_analyser.py $(ls -1 -v ./massif.out.* | tail -n 1)

# Monitoring CPU
pipenv run python monitor/monitor_cpu.py "python main.py --steps $PAS_STEPS"

# Monitoring simultaneous requests performance
pipenv run python test/test_simultaneous_requests.py --min_processes 100 --max_processes 1000 --step_processes 100  # TODO : Broken
```
-->
