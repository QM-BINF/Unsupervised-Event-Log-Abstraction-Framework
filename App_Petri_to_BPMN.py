from lib2to3.pytree import convert
import pm4py
from glob import glob
import os
import tqdm

def convert_for_dir(dir):
    if dir == "LowLevel":
        files = glob(os.path.join("PetriNet", dir, "*.pnml"))
    else:
        files = glob(os.path.join("PetriNet", dir, "*" + dir + ".pnml"))
    os.makedirs(os.path.join("BPMN", dir), exist_ok=True)

    for file in tqdm.tqdm(files, f"Converting {dir}"):
        name = os.path.basename(file).replace(".pnml", ".bpmn")
        net, im, fm = pm4py.read_pnml(file)
        bpmn = pm4py.convert_to_bpmn(net, im, fm)
        pm4py.write_bpmn(bpmn, os.path.join("BPMN", dir, name))

if __name__ == "__main__":
    for dir in ["LowLevel", "LPM", "Massimiliano"]:
        convert_for_dir(dir)