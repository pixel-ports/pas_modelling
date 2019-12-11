# PIXEL Port Activity Scenario Modelling

This repository implements the PAS modelling presented in the MTC paper : https://www.dropbox.com/s/6z2e854bxz9jtur/MTC2019_SIMON_LACALLE.pdf?dl=0.

## Production

## Getting started

You'll need docker to run the PAS docker image : https://docs.docker.com/install/linux/docker-ce/ubuntu/

One run of the PAS start the container, takes inputs from the `inputs` folder, outputs results files to the `outputs` folder and exits.  
For the run, you'll have to mount your `inputs` and `outputs` folders, and specify in-container filepaths in the `.env` file. You can also leave everything as default and run a demo with the following commands :

```bash
docker build -t pas .
rm -rf inputs outputs
mkdir inputs outputs
cp data_models/inputs/*.json inputs/
docker run --env-file .env -v $(pwd):/pas pas python3 main.py --steps 1 2 3 4
```

This builds the docker image, create `inputs`/`outputs` folders and fill `inputs` with the default data_models. It then runs the complete PAS, outputs results to the `outputs` folder and exits.

## Development

### Getting started

On linux, run the following commands in order to get started :

```bash
sudo apt-get install python3 python3-dev
sudo pip install pipenv  # installs pipenv globally
pipenv install  # installs the required dependencies
git config core.hooksPath .githooks  # defines project git hooks folder
```
Then update files in `data/` according to your port needs or leave them as they are, then start the process :

```bash
pipenv run python main.py --steps 1 2 3 4
```

### Generate fake data for demonstration purpose

```bash
pipenv run python tools/fake_pas_generation.py
pipenv run jupyter-notebook tools/demonstration.ipynb
```

### Statistics for WP8 Product Quality Model

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
