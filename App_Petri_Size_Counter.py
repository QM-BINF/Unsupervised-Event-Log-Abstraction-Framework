import pm4py
from src.Evaluation.PetriNetCounter import PetriNetCounter
from glob import glob
from tqdm import tqdm

import os

filename = "Stats/HighLevel_petri_size.csv"

def perform_for_level(level):
    files = glob(os.path.join("PetriNet", level, "*" + level + ".pnml"))
    
    with open(filename, mode = "a") as csv:
        for file in tqdm(files, level):
            id, *junk = os.path.basename(file).split("-")
            del junk

            petri, im, fm = pm4py.read_pnml(file)
            counter = PetriNetCounter([petri, im, fm])

            csv.write("\n")
            csv.write(f"{id},{level},{counter.get_petri_size()}")

    pass

if __name__ == "__main__":
    with open(filename, mode = "w") as csv:
        csv.write("id,level,transitions")

    perform_for_level("LPM")
    perform_for_level("Massimiliano")