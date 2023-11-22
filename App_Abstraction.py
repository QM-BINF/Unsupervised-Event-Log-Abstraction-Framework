from src.Abstraction.Abstractor import Abstractor

import logging
from logging import log
import pm4py
import pandas as pd

import os
import platform
import sys
import time

# Source code to execute session-based event log abstraction
# For this code to run, you need to downgrade pm4py to 2.2.2 and graphviz to 0.15.0

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG, filename='src/Abstraction/eventabstraction.log', filemode='w', format='%(levelname)s - %(message)s')

    log(logging.DEBUG, f"OS version:\t{platform.platform()}\nPython version:\t{sys.version}\nPM4Py version:\t{pm4py.__version__}\n")

    #Prepare the log list
    data = pd.read_csv("EventLogs.csv")
    logs = [x for x in data["log"]]
    # logs = [x for x in data["log"] if not os.path.isfile(os.path.join(".AbstractedLogs", x.replace(".xes.gz", "_AbstractedLog.xes")))]
    print(logs)

    #Parameters for K-Means
    # params = {
    #     "alg":"kmeans"
    #     "num" :20, #Number of clusters to create
    #     "assignNoisy" : True
    # }

    params = {
        "alg":"dbscan",
        "minsamples":100,
        "eps":0.75,
        "assignNoisy" : True
    }

    # Create output csv for time logging
    if not os.path.isfile("DurationLogging.csv"):
        with open("DurationLogging.csv", "w") as file:
            print("Creating DurationLogging.csv")
            file.write("log,algo_duration")

    # Start ELA
    for EventLog in logs:
        print(f"===========\n{EventLog}")
        algo_start = time.time()

        #Threshold is the time that determines when a new session starts (in minutes)
        filename = EventLog.replace(".gz", "")
        file = os.path.join("Logs", "gz", filename + ".gz")
        abstractor = Abstractor(fileName = file, attrNames = [], threshold = 5, parallel = True)

        #Encoding based on frequency of occurrences 
        abstractor.encode('freq')

        #Encoding based on time (slower, but necessary when the duration of the activities is more important than the sole occurrence)
        #abstractor.encode('time')


        # # epsEstimate(abstractor.encodedLog,imgpath)
        # # minPointsEstimate(abstractor.encodedLog, 0.07,imgpath)
        # # elbow(abstractor.encodedLog,10,40,imgpath)

        #create clusters and compute centroids
        y_pred,centers = abstractor.cluster(params)

        #Visualize the clusters and centroids on a heatmap: A file "test.png" is created in the current directory
        #abstractor.betterPlotting(centers,y_pred,"test",params)

        #Abstraction of the event log. The abstract event log will be created in "working directory/AbstractedLogs/""
        #The logs related to each cluster (and high-level activity) is created in the subdirectory "Clusters"
        abstractor.convertLog(centers, y_pred, path = '.AbstractedLogs', exportSes = True)

        print(f"Total algorithm time for {filename}: {round((time.time() - algo_start) / 60, 2)} minutes")
        with open("DurationLogging.csv", "a") as file:
            file.write(f"\n{EventLog},{time.time() - algo_start}")