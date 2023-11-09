from src.Simulation.tree_generator import TreeGenerator
from src.Simulation.simulation_model import SimulationModel

import pm4py

import src.Simulation.utils as utils
import logging
from logging import log

import os
import platform
import sys
import random

# Source code to perform process simulation via BPSimPy. The generated model is later fed to L-Sim (no source code available)

if __name__ == "__main__":
    logging.basicConfig(
        level = logging.INFO,
        filename='src/Simulation/bpsimulation.log',
        filemode='w',
        format='%(levelname)s - %(message)s'
    )

    log(logging.INFO, f"OS version:\t{platform.platform()}\nPython version:\t{sys.version}\nPM4Py version:\t{pm4py.__version__}\n")

    utils.clean_filestruct()

    tree_size = (15, 85, 150)
    n = 400
    word = "files" if n > 1 else "file"
    logging.log(logging.INFO, f"Construction of {n} BPSim simulation {word} started. Tree size set to {tree_size}.")

    for i in range(n):
        # Start with the generation of process models
        tree_gen = TreeGenerator(tree_size)
        tree_gen.write_bpmn(i + 1)
        tree_gen.write_processtree(i + 1)

        # log(logging.INFO, f"Process Tree and BPMN files generated and written to disk. Iteration {i + 1} generated a model with {len(tree_gen.get_tree()._get_leaves())} activities.")

        # Construct the simulation model
        sim = SimulationModel(os.path.join("BPMN", tree_gen.bpmn_file))
        simulation_length = tree_gen.calc_simulation_length()
        sim.create_scenario(duration_days = simulation_length)
        sim.set_bpmn_model(tree_gen.get_bpmn())

        # Populate the simulation model with different parameters
        # Case Arrival Rate
        params = {
            "distribution": "TruncatedNormalDistribution",
            "min": random.uniform(3, 7),
            "mean": random.uniform(8, 17),
            "max": random.uniform(20, 45),
            "sd": random.randint(1,4)
        }
        sim.set_case_arrival_rate(params)

        # Task Wait and Processing Times
        tasks = sim.get_bpmn_task_ids()
        for task in tasks:
            sim.set_task_distributions(task, utils.get_params_wait(), utils.get_params_processing())
        
        # Gateway outgoing edge probabilities
        gates = sim.get_bpmn_xor_gateways()
        for gate in gates:
            sim.set_gateway_probabilities(gate)

        # Rename and move this BPSim model before moving to the next iteration
        sim.rename('BPSim')

        log(logging.INFO, f"Iter {i + 1}\t\tSimulation length: {simulation_length} days\t\tActivity classes: {tree_gen.get_activity_count()}")
        with open("src/Simulation/LogGeneration.csv", "a") as file:
            seq, cho, par = tree_gen.get_parameters()
            file.write("\n")
            file.write(f"{i + 1},{seq},{cho},{par},{tree_gen.get_activity_count()},{simulation_length}")