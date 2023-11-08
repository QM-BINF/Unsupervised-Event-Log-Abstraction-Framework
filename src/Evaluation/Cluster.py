import pm4py
from pm4py.objects.log.importer.xes.importer import apply as log_importer
import os

params_import_log = {"show_progress_bar": False}
params_export_log = {"show_progress_bar": False, "compress": True}

class Cluster:
    def __init__(self, path:str) -> None:
        self.cluster = log_importer(path, parameters = params_import_log)
        self.pn = pm4py.discover_petri_net_inductive(self.cluster, noise_threshold=0.20)
        self.index = os.path.basename(path).replace("cluster", "").replace(".xes.gz", "")
        self.index = int(self.index)

        self.transitions_count = 0
        self.transitions_hidden_count = 0
        self.calculate_net_size()

    def calculate_net_size(self):
        count = 0
        hidden = 0

        net, im, fm = self.pn

        for t in net.transitions:
            if t.label is None:
                hidden += 1
            else:
                count += 1
            
        self.transitions_count = count
        self.transitions_hidden_count = hidden

    def get_size_of_cluster_net(self):
        net, im, fm = self.pn

    def get_petri(self):
        return self.pn