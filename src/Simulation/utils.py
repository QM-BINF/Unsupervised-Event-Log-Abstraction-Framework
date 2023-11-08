"""This module contains support functions to create BPSim files.

- Generating process trees
- Setting up data structure for BPSim
- Cleaning and prepping file structure
"""

import os
import shutil
import logging
import random

def clean_filestruct():
    logging.log(logging.DEBUG, "Deleting the output directories - starting new iterations.")
    for directory in ("BPMN", "BPSim", "ProcessTree"):
        if os.path.exists(os.path.join(directory)):
            shutil.rmtree(directory, ignore_errors = True)
        

    logging.log(logging.DEBUG, "Preparing file structure: creating BPMN, ProcessTree and BPSim directories.")
    os.mkdir("BPMN")
    os.mkdir("BPSim")
    os.mkdir("ProcessTree")

    n = 0
    for file in os.scandir('.'):
        if ("BPMN.xml" in file.name or "-BPMN-" in file.name) and (not ".pdf" in file.name and not ".py" in file.name):
            os.remove(file)
            n += 1
    logging.log(logging.DEBUG, f"Removed {n} working files in the working directory.")

    with open("src/Simulation/LogGeneration.csv", mode = "w") as file:
        file.write("id,sequence,choice,parallel,activities,simulation_duration")

    logging.log(logging.DEBUG, "Files removed and directories created. Ready for BPSim generation\n")

def get_params_wait():
    return {
                "distribution": "TruncatedNormalDistribution",
                "min": random.uniform(4, 6),
                "mean": random.uniform(7, 14),
                "max": random.uniform(20, 35),
                "sd": random.randint(2, 5)
           }
        
def get_params_processing():
    min = random.uniform(3, 20)
    mean = random.uniform(min + random.uniform(1, 8), min + random.uniform(12, 20))
    max =  random.uniform(mean  + random.uniform(5, 8), mean + random.uniform(15, 25))
    return {
                "distribution": "TruncatedNormalDistribution",
                "min": min,
                "mean": mean,
                "max": max,
                "sd": random.randint(2, 6)
           }