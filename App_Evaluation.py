from enum import Enum
from src.Evaluation.LogAbstraction import LogAbstraction

import os, sys
import logging

if __name__ == "__main__":
    # logging.basicConfig(level = logging.DEBUG, filename='src/Evaluation/evaluation.log', filemode='w', format='%(levelname)s - %(message)s')

    # logging.log(logging.DEBUG, f"OS version:\t{platform.platform()}\n        Python version:\t{sys.version}\n        PM4Py version:\t{pm4py.__version__}\n")

    try:
        logfile = sys.argv[1]
    except:
        logfile = "1-BPSim-0.34-0.51-0.15.xes.gz"
        extension = ".xes.gz"
    logging.log(logging.DEBUG, f"{sys.argv[0]} {logfile}\n")
    basename = logfile.replace(extension, "")

    print(f"=== {basename} ===")

    # Load low-level event log
    log = LogAbstraction(os.path.join("Logs", ".gz", logfile))

    # Work on the LPM logs
    if os.path.isfile(os.path.join("Logs", "LPM", basename + "_LPM" + extension)):
        log.load_LPM()
        log.expand_net("LPM")


    # Work on the Massimiliano logs
    if os.path.isfile(os.path.join("Logs", "MASSIMILIANO", basename + "_AbstractedLog.xes.gz")):
        log.load_Massimiliano()
        log.expand_net("Massimiliano")

    # Do the conformance checks for all available models in de LogAbstraction object
    log.conformance_check_replay()

    print("Starting Simplicity computations")
    log.simplicity()
    print("Simplicity done")

    # Write created Petri Nets to disk
    log.write_petri_output()
    log.write_csv_output()
    log.write_simplicity()
    # logging.log(logging.DEBUG, f"The Massimiliano_ExpandedNet contains {len(log.PN_Massimiliano_Expanded[0].transitions)} transitions and {len(log.PN_Massimiliano_Expanded[0].places)} places.")