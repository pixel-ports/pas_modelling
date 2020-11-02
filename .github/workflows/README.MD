# GitHub actions configuration

Informations for GitHub actions configuration

## Logic
On "Develop" branch:
- Tests involve pure python code (not the docker image). 
- In PAS_builder, the main try/except security sould be off (#FIXME, that's discusting!)
- Each push should at least pass a minimal test : (develop_minimal_test). 
- Each time a feature branch is merge on Develop, a feature specific test should be added and be pass by every futur push on Develop

## develop_minimal_test
Test if :
[x] dependencies are clear
[x] PAS_builder run without error on pipeline "local_PAS_instance" (e.g. without IH interactions: a local PAS_instance with all "force-input" (no IH read) and module IH_writer disabled) => "python3 ./main.py --pipeline=local_PAS_instance, --OT_input=local_PAS_instance"
[] PAS_builder run without error on pipeline "test_PAS_instance" (e.g. with IH interactions: a local PAS_instance with manualy edited url & index, and module exporting output to IH)
