from typing import Union
from pm4py.objects.bpmn.obj import BPMN
import BPSimpy as bps
from lxml import etree

import os
import datetime

class SimulationModel():
    """Class which controls the construction of a BPSim simulation model."""
    def __init__(self, bpmn_model : str):
        self.bpsim = bps.BPSim(bpmn_model)
        self.bpsim.addXmlns(name = 'lsim', value = "urn:lanner.simulation.lsim.model.data")
        self.bpsim_name = os.path.basename(bpmn_model).replace("BPMN", "BPSim")
        self.bpsim_name = self.bpsim_name.replace(".bpmn", ".xml")

        self.tree = etree.Element("TaskConfiguration")
        self.child = etree.SubElement(self.tree,"EventLog")

    def create_scenario(self, duration_days : int, id : str = "S0", name : str = "BPMN Simulation Model", author : str = "Greg Van Houdt - Hasselt University"):
        self.scenario : bps.Scenario = self.bpsim.addScenario(id = id, name = name, author = author)
        self.scenario.addScenarioParameters()
        self.scenario.addDuration(datetime.timedelta(days = duration_days))

    def rename(self, path : str = '.'):
        os.rename("BPSIM_output.xml", os.path.join(path, self.bpsim_name))

    def set_bpmn_model(self, bpmn : BPMN):
        self.bpmn = bpmn
        self.__data_dict = self.__construct_dict()

    def __construct_dict(self):
        res = {
            "Tasks" : [],
            "StartEvent" : "",
            "Xor_gates" : []
        }
        for node in self.get_bpmn_nodes():
            if type(node) is BPMN.Task:
                res["Tasks"].append({
                    "id" : node.get_id(),
                    "name" : node.get_name()
                })

            elif type(node) is BPMN.StartEvent:
                res["StartEvent"] = node.get_id()

            elif type(node) is BPMN.ExclusiveGateway:
                res["Xor_gates"].append(node)

        return res

    def get_bpmn_nodes(self):
        return self.bpmn.get_nodes()

    def get_bpmn_tasks(self):
        return self.__data_dict["Tasks"]

    def get_bpmn_task_ids(self):
        set = []
        for d in self.get_bpmn_tasks():
            set.append(d["id"])
        return set

    def get_bpmn_task_names(self):
        set = []
        for d in self.get_bpmn_tasks():
            set.append(d["name"])
        return set
    
    def get_bpmn_start_event(self):
        return self.__data_dict["StartEvent"]

    def get_bpmn_xor_gateways(self):
        return self.__data_dict["Xor_gates"]

    def set_case_arrival_rate(self, params : dict):
        elementParam : bps.ElementParameter = self.scenario.getElementParameters(self.get_bpmn_start_event())
        elementParam.addInterTriggerTimer(
            nameDistribution = params["distribution"],
            min = params["min"],
            mean = params["mean"],
            max = params["max"],
            standardDeviation = params["sd"]
        )

    def set_task_distributions(self, task_id : str, params_wait : dict, params_processing : dict):
        elementParam : bps.ElementParameter = self.scenario.getElementParameters(task_id)
        elementParam.addWaitTime(
            nameDistribution = params_wait["distribution"],
            min = params_wait["min"],
            mean = params_wait["mean"],
            max = params_wait["max"],
            standardDeviation = params_wait["sd"]
        )
        elementParam.addProcessingTime(
            nameDistribution = params_processing["distribution"],
            min = params_processing["min"],
            mean = params_processing["mean"],
            max = params_processing["max"],
            standardDeviation = params_processing["sd"]
        )
        elementParam.addVendorExtension("l-sim-task-configuration-v1", [self.tree])

    def set_gateway_probabilities(self, gateway : BPMN.ExclusiveGateway):
        outgoing = gateway.get_out_arcs()
        p = 1 / len(outgoing)

        for out in outgoing:
            elementParam : bps.ElementParameter = self.scenario.getElementParameters("id" + str(out.get_id()))
            elementParam.addProbability(p)