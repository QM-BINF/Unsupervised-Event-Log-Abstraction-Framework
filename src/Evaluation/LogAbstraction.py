from glob import glob
from src.Evaluation.Cluster import Cluster
from src.Evaluation.ModelExpander import ModelExpander

import pm4py
from pm4py.objects.log.importer.xes.importer import apply as log_importer
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.log.obj import EventLog
from pm4py.algo.evaluation.replay_fitness import evaluator as fitness_evaluator
from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_algoritmh

import os
import logging
from typing import Tuple

from src.Evaluation.Pattern import Pattern

params_import_log = {"show_progress_bar": False}
params_export_log = {"show_progress_bar": False, "compress": True}

class LogAbstraction:
    def __init__(self, path:str) -> None:
        self.name = os.path.basename(path).replace(".xes", "").replace(".gz", "")

        self.log_original = log_importer(path, parameters = params_import_log)
        self.log_LPM = None
        self.log_COBPAM = None
        self.log_Massimiliano = None

        self.PN_original = LogAbstraction.inductive_miner(self.log_original)
        self.PN_LPM = None
        self.PN_COBPAM = None
        self.PN_Massimiliano = None

        self.PN_LPM_Expanded = None
        self.PN_COBPAM_Expanded = None
        self.PN_Massimiliano_Expanded = None

        self.LPM = None
        self.COBPAM = None
        self.Clusters = None

        self.num_LPM_abstracted = None
        self.num_COBPAM_abstracted = None
        self.num_Massimiliano_abstracted = None

        self.conformance_low = (None, None)
        self.conformance_LPM = (None, None)
        self.conformance_COBPAM = (None, None)
        self.conformance_Massimiliano = (None, None)

        self.simplicity_low = None
        self.simplicity_LPM = None
        self.simplicity_COBPAM = None
        self.simplicity_Massimiliano = None

        # logging.log(logging.DEBUG, f"{self.name}: Initialised with low-level log and petri net.")

    def load_LPM(self) -> None:
        # Load the high-level log and mine the PetriNet
        name = self.name + "_LPM.xes.gz"
        name = self.name + "_LPM.xes"
        self.log_LPM = log_importer(os.path.join("Logs", "LPM", name), parameters = params_import_log)
        self.PN_LPM = LogAbstraction.inductive_miner(self.log_LPM)

        # Load all mined patterns into memory
        # files = glob(os.path.join("PetriNet", "LPM", "Patterns", self.name + "*.pnml"))
        files = glob(os.path.join("PetriNet", "LPM", self.name + "*.pnml"))
        res = []
        for file in files:
            res.append(Pattern(file))
        
        if len(res) == 0: res = None
        self.LPM = res

        print("= LPM LOADED =")

    def load_COBPAM(self) -> None:
        pass

    def load_Massimiliano(self) -> None:
        name = self.name + "_AbstractedLog.xes.gz"
        self.log_Massimiliano = log_importer(os.path.join("Logs", "MASSIMILIANO", name), parameters = params_import_log)
        self.PN_Massimiliano = LogAbstraction.inductive_miner(self.log_Massimiliano)
        # logging.log(logging.DEBUG, f"{self.name}: High-level event log mined by Massimiliano is loaded.")

        path = os.path.join("Logs", "MASSIMILIANO", "Clusters", self.name)
        if os.path.isdir(path):
            res = []

            for file in os.scandir(path):
                if file.is_file() and ".xes" in file.name:
                    res.append(Cluster(file.path))

            self.clusters = res
            # logging.log(logging.DEBUG, f"{self.name}: Massimiliano's clusters loaded in memory and Petri Nets are mined.")

            print("= MASSIMILIANO LOADED =")
        else:
            # logging.log(logging.DEBUG, f"{self.name}: Directory {path} does not exist. Cannot load clusters.")
            self.clusters = None

    def expand_net(self, technique:str) -> None:
        if technique.upper() == "LPM":
            expander = ModelExpander(self.name, self.PN_LPM, self.LPM)
            expander.lpm()
            self.PN_LPM_Expanded = expander.get_expanded_net()
            self.num_LPM_abstracted = expander.get_num_abstracted_patterns()
        elif technique.upper() == "COBPAM":
            expander = ModelExpander(self.name, self.PN_COBPAM, self.COBPAM)
            expander.cobpam()
            self.PN_COBPAM_Expanded = expander.get_expanded_net()
            self.num_COBPAM_abstracted = expander.get_num_abstracted_patterns()
        elif technique.upper() == "MASSIMILIANO":
            expander = ModelExpander(self.name, self.PN_Massimiliano, self.clusters)
            expander.massimiliano()
            self.PN_Massimiliano_Expanded = expander.get_expanded_net()
            self.num_Massimiliano_abstracted = expander.get_num_abstracted_patterns()
        else:
            # logging.log(logging.WARNING, f"{self.name}: Argument 'technique' must be in ['LPM', 'COBPAM', 'MASSIMILIANO]")
            pass
    
    def get_cluster_nets(self) -> list[Tuple[PetriNet, Marking, Marking]]:
        res = []
        for cluster in self.clusters:
            res.append(cluster.get_petri())
        return res

    def get_logs(self) -> dict[str, EventLog]:
        return {"log_Original":self.log_original, "log_LPM":self.log_LPM, "log_COBPAM":self.log_COBPAM, "log_Massimiliano":self.log_Massimiliano}

    def get_petri(self) -> dict[str, Tuple[PetriNet, Marking, Marking]]:
        return {"PN_Original":self.PN_original, "PN_LPM":self.PN_LPM, "PN_COBPAM":self.PN_COBPAM, "PN_Massimiliano":self.PN_Massimiliano}

    def get_petri_expanded(self) -> dict[str, Tuple[PetriNet, Marking, Marking]]:
        return {"PN_LPM_Expanded": self.PN_LPM_Expanded, "PN_COBPAM_Expanded": self.PN_COBPAM_Expanded, "PN_Massimiliano_Expanded":self.PN_Massimiliano_Expanded}

    def conformance_check_replay(self):
        checks = [self.PN_original, self.PN_LPM_Expanded, self.PN_COBPAM_Expanded, self.PN_Massimiliano_Expanded]
        results = []
        i = 0
        out = ["Low level", "LPM", "COBPAM", "Massimiliano"]

        for petri in checks:
            if petri is not None and type(petri) == tuple:
                net, im, fm = petri
                fit = fitness_evaluator.apply(self.log_original, net, im, fm,
                                              variant=fitness_evaluator.Variants.TOKEN_BASED, parameters={"show_progress_bar":False})
                fit_log = fit["average_trace_fitness"]
                print(f"{self.name}: Average Trace Fitness for the {out[i]} Petri Net = {fit_log}")
                del fit

                prec = precision_evaluator.apply(self.log_original, net, im, fm,
                                                 variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN, parameters={"show_progress_bar":False})
                print(f"{self.name}: Precision metric for the {out[i]} Petri Net = {prec}")

                results.append((fit_log, prec))

                del fit_log, prec
                i += 1
            else:
                results.append((None, None))
                i += 1

        self.conformance_low = results[0]
        self.conformance_LPM = results[1]
        self.conformance_COBPAM = results[2]
        self.conformance_Massimiliano = results[3]

    def conformance_check_alignment(self, MP = True) -> None:
        checks = [self.PN_original, self.PN_LPM_Expanded, self.PN_COBPAM_Expanded, self.PN_Massimiliano_Expanded]
        results = []
        i = 0
        out = ["Low level", "LPM", "COBPAM", "Massimiliano"]

        for petri in checks:
            if petri is not None and type(petri) == tuple:
                net, im, fm = petri
                fit = pm4py.fitness_alignments(self.log_original, net, im, fm, multi_processing=MP)
                fit_log = fit["log_fitness"]
                prec = pm4py.precision_alignments(self.log_original, net, im, fm, multi_processing=MP)
                results.append((fit_log, prec))

                i += 1
            else:
                results.append((None, None))
                i += 1

        self.conformance_low = results[0]
        self.conformance_LPM = results[1]
        self.conformance_COBPAM = results[2]
        self.conformance_Massimiliano = results[3]

    def simplicity(self):
        checks = [self.PN_original, self.PN_LPM, self.PN_COBPAM, self.PN_Massimiliano]
        results = []
        i = 0
        out = ["Low level", "LPM", "COBPAM", "Massimiliano"]

        for petri in checks:
            if petri is not None and type(petri) == tuple:
                net, im, fm = petri
                simp = simplicity_algoritmh.apply(net)
                print(f"{self.name}: Net Simplicity for the {out[i]} Petri Net = {simp}")
                results.append(simp)
                i += 1
            else:
                results.append(None)
                print(f"{out[i]} simplicity not computed. No net found.")
                i += 1

        self.simplicity_low = results[0]
        self.simplicity_LPM = results[1]
        self.simplicity_COBPAM = results[2]
        self.simplicity_Massimiliano = results[3]

    def visualise(self, technique:str) -> None:
        if technique.upper() == "LPM":
            if self.PN_LPM is not None:
                net, im, fm = self.PN_LPM
                pm4py.view_petri_net(net, im, fm)

            if self.PN_LPM_Expanded is not None:
                net, im, fm = self.PN_LPM_Expanded
                pm4py.view_petri_net(net, im, fm)

        if technique.upper() == "COBPAM":
            if self.PN_COBPAM is not None:
                net, im, fm = self.PN_COBPAM
                pm4py.view_petri_net(net, im, fm)

            if self.PN_COBPAM_Expanded is not None:
                net, im, fm = self.PN_COBPAM_Expanded
                pm4py.view_petri_net(net, im, fm)

        if technique.upper() == "MASSIMILIANO":
            if self.PN_Massimiliano is not None:
                net, im, fm = self.PN_Massimiliano
                pm4py.view_petri_net(net, im, fm)

            if self.PN_Massimiliano_Expanded is not None:
                net, im, fm = self.PN_Massimiliano_Expanded
                pm4py.view_petri_net(net, im, fm)

    def write_csv_output(self):
        # Check if the output path already exists. Create it if not
        path = os.path.join("Stats", self.name + ".csv")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, mode="w") as file:
            file.write("id,fitness,precision,LPM_activities,LPM_abstractions,LPM_fitness,LPM_precision,COBPAM_activities,COBPAM_abstractions,COBPAM_fitness,COBPAM_precision,Massimiliano_activities,Massimiliano_abstractions,Massimiliano_fitness,Massimiliano_precision")
        
        # we need the log id (merge with src/Simulation/LogGeneration.csv afterwards), low-level transitions, low-level conformance,
        # LPM transitions, LPM abstractions, LPM conformance, COBPAM transitions, COBPAM abstractions, COBPAM conformance,
        # Massimiliano transitions, Massimiliano abstractions, Massimiliano conformance
        id, *junk = self.name.split("-")
        del junk

        fit,prec = LogAbstraction.unpack_conformance(self.conformance_low)
        lpm_fit, lpm_prec = LogAbstraction.unpack_conformance(self.conformance_LPM)
        cobpam_fit, cobpam_prec = LogAbstraction.unpack_conformance(self.conformance_COBPAM)
        massi_fit, massi_prec = LogAbstraction.unpack_conformance(self.conformance_Massimiliano)

        lpm_trans = LogAbstraction.get_petri_size(self.PN_LPM)
        cobpam_trans = LogAbstraction.get_petri_size(self.PN_COBPAM)
        massi_trans = LogAbstraction.get_petri_size(self.PN_Massimiliano)

        lpm_abs = self.num_LPM_abstracted or "NA"
        cobpam_abs = self.num_COBPAM_abstracted or "NA"
        massi_abs = self.num_Massimiliano_abstracted or "NA"

        with open(path, mode="a") as file:
            file.write("\n")
            file.write(f"{id},{fit},{prec},{lpm_trans},{lpm_abs},{lpm_fit},{lpm_prec},{cobpam_trans},{cobpam_abs},{cobpam_fit},{cobpam_prec},{massi_trans},{massi_abs},{massi_fit},{massi_prec}")
    
    def write_simplicity(self):
        # Check if the output path already exists. Create it if not
        path = os.path.join("Simplicity", self.name + ".csv")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, mode="w") as file:
            file.write("id,low,lpm,cobpam,massimiliano")

        id, *junk = self.name.split("-")
        del junk

        low = self.simplicity_low or "NA"
        lpm = self.simplicity_LPM or "NA"
        cob = self.simplicity_COBPAM or "NA"
        mas = self.simplicity_Massimiliano or "NA"
        
        with open(path, mode="a") as file:
            file.write("\n")
            file.write(f"{id},{low},{lpm},{cob},{mas}")



    def write_petri_output(self):
        paths = [os.path.join("PetriNet", "LowLevel"),
            os.path.join("PetriNet", "LPM"),
            os.path.join("PetriNet", "COBPAM"),
            os.path.join("PetriNet", "Massimiliano")]
        
        for path in paths:
            try:
                os.makedirs(path,exist_ok=True)
            except OSError:
                print (f"Creation of the directory {path} failed")

        attributes = self.get_petri() | self.get_petri_expanded()

        for key,value in attributes.items():
            exportname = self.name
            target = None

            if "Original" in key:
                target = os.path.join("PetriNet", "LowLevel")
            elif "LPM" in key:
                target = os.path.join("PetriNet", "LPM")
                exportname += "_LPM"
            elif "COBPAM" in key:
                target = os.path.join("PetriNet", "COBPAM")
                exportname += "_COBPAM"
            elif "Massimiliano" in key:
                target = os.path.join("PetriNet", "MASSIMILIANO")
                exportname += "_Massimiliano"

            if "Expanded" in key:
                exportname += "_ExpandedNet"
            
            exportname += ".pnml"

            if value is not None:
                net, im, fm = value
                pm4py.write_petri_net(net, im, fm, os.path.join(target, exportname))

        # logging.log(logging.DEBUG, f"{self.name}: Petri Nets exported to disk.")
    
    @staticmethod
    def unpack_conformance(input:tuple) -> tuple:
        if input is None or len(input) != 2:
            return "NA", "NA"

        elif input[0] is None and input[1] is None:
            return "NA", "NA"
        else:
            return input

    @staticmethod
    def get_petri_size(input:Tuple[PetriNet,Marking,Marking]):
        if input is None:
            return "NA"
        else:
            return len(input[0].transitions)


    @staticmethod
    def inductive_miner(log:EventLog) -> Tuple[PetriNet,Marking,Marking]:
        return pm4py.discover_petri_net_inductive(log, noise_threshold=0.20)
        

    def reset(self):
        self.log_LPM = None
        self.log_COBPAM = None
        self.log_Massimiliano = None

        self.PN_LPM = None
        self.PN_COBPAM = None
        self.PN_Massimiliano = None

        self.PN_LPM_Expanded = None
        self.PN_COBPAM_Expanded = None
        self.PN_Massimiliano_Expanded = None

        self.LPM = None
        self.COBPAM = None
        self.Clusters = None

        # logging.log(logging.DEBUG, f"{self.name}: Attributes are reset to None values.")

    def __str__(self) -> str:
        res = f"Log Evaluation for {self.name} containing {len(self.log_original)} traces"
        return res