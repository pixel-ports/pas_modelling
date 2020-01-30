import logging

from .steps.Step1 import Step1
from .steps.Step2 import Step2
from .steps.Step3 import Step3
from .steps.Step4 import Step4

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger("pas-modelling")

def run(steps, cargo_handling_requests=None, rules=None, supplychains=None, resources=None):
    pas = cargo_handling_requests  # legacy renaming

    if 1 in steps:
        logger.info("--- Step 1 ---")
        step1 = Step1(pas)
        pas = step1.run()
    
    if 2 in steps:
        logger.info("--- Step 2 ---")
        step2 = Step2(pas, rules, supplychains)
        pas = step2.run()

    if 3 in steps:
        logger.info("--- Step 3 ---")
        step3 = Step3(pas, supplychains, resources)
        pas = step3.run()

    if 4 in steps:
        logger.info("--- Step 4 ---")
        step4 = Step4(pas, resources)
        pas = step4.run()
        
    return pas