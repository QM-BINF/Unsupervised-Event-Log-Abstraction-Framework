import pm4py
from pm4py.objects.log.importer.xes.importer import apply as log_importer
import os

params_import_log = {"show_progress_bar": False}
params_export_log = {"show_progress_bar": False, "compress": True}

class Pattern():
    def __init__(self, path:str) -> None:
        *junk, n = os.path.basename(path).split("-")
        self.name = n.replace(".pnml", "")
        self.net = pm4py.read_pnml(path)

        del junk, n

    def calculate_net_size(self):
        count = 0
        hidden = 0

        net, im, fm = self.net

        for t in net.transitions:
            if t.label is None:
                hidden += 1
            else:
                count += 1
            
        self.transitions_count = count
        self.transitions_hidden_count = hidden