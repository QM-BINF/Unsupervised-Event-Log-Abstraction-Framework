import pm4py
from pm4py.objects.log.util import dataframe_utils
import pandas as pd

import logging

import os
import platform
import sys

def restructure_pd_to_eventlog(df : pd.DataFrame) -> pd.DataFrame:
    # Drop unnecessary columns & rename columns to match with the PM expectations
    df.drop(columns = ['Scenario', 'Replication', 'Arrived', 'Resources'], inplace = True)
    df.rename(columns = {"TokenId" : "case:concept:name", "Element" : "concept:name", "Started" : "start", "Completed" : "complete"}, inplace = True)

    # Unpivot from wide to long format: we need the lifecycles and timestamps in separate rows
    df = df.melt(("case:concept:name", "concept:name"), var_name = "lifecycle:transition", value_name = "time:timestamp")
    df = dataframe_utils.convert_timestamp_columns_in_df(df)
    df.sort_values('time:timestamp', inplace = True)

    return df

if __name__ == "__main__":
    logging.basicConfig(
        level = logging.DEBUG,
        filename='Logs/.xes/Event Log Translation.log',
        filemode='w',
        format='%(levelname)s - %(message)s'
    )

    logging.log(logging.DEBUG, f"OS version:\t{platform.platform()}\nPython version:\t{sys.version}\nPM4Py version:\t{pm4py.__version__}\n")


    # Start the iterations: for each log file in Logs
    for log in os.scandir(os.path.join("Logs", ".log")):
        logname : str = os.path.basename(log)
        xesname = logname.replace(".log", ".xes")

        df = pd.read_table(os.path.join("Logs", ".log", logname), sep = "\t")
        df = restructure_pd_to_eventlog(df)

        eventlog = pm4py.convert_to_event_log(df)
        pm4py.write_xes(eventlog, os.path.join("Logs", ".xes", xesname))

        logging.log(logging.DEBUG, f"Log {logname} successfully translated to XES and exported to disk.")