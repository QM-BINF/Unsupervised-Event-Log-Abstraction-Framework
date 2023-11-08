import pm4py
from pm4py.objects.bpmn.obj import BPMN
from pm4py.algo.simulation.tree_generator import algorithm as pt_generator

import os
import random

from typing import Tuple
from typing import Union

class TreeGenerator():
    """Implementation for generating a process tree (PM4Py implementation), making computations on and in it, and writing it to disk."""
    def __init__(self, tree_size : Tuple[int, int, int]):
        self.generate_process_tree(tree_size)
        self.convert_to_bpmn()

        self.bpmn_file = None
        self.pt_file = None

    def generate_process_tree(self, tree_size : Tuple[int, int, int]):
        self.__tree_size = tree_size
        sequence = round(random.uniform(0.3, 0.6), 2)
        parallel = round(random.uniform(0.1, 0.3), 2)
        choice = round(1 - sequence - parallel, 2)

        min, mode, max = tree_size

        parameters = {}
        parameters['min'] = min
        parameters['mode'] = mode
        parameters['max'] = max
        parameters['no_models'] = 1 
        parameters['sequence'] = sequence
        parameters['choice'] = parallel
        parameters['parallel'] = choice
        parameters['loop'] = 0
        parameters['or'] = 0
        parameters['silent'] = 0
        parameters['duplicate'] = 0
        parameters['lt_depencency'] = 0
        parameters['infrequent'] = 0
        parameters['unfold'] = 0
        parameters['max_repeat'] = 0

        self.process_tree = pt_generator.apply(parameters=parameters)
        self.sequence = sequence
        self.choice = choice
        self.parallel = parallel

    def get_tree(self):
        return self.process_tree

    def get_parameters(self):
        return self.sequence, self.choice, self.parallel

    def get_activity_count(self):
        nodes = self.bpmn.get_nodes()
        n = 0
        for node in nodes:
            if type(node) == BPMN.Task:
                n += 1
        return n

    def convert_to_bpmn(self):
        self.bpmn = pm4py.convert_to_bpmn(self.process_tree)
        self.__set_gateway_directions()

    def __set_gateway_directions(self):
        for node in self.bpmn.get_nodes():
            if type(node) in {BPMN.ExclusiveGateway, BPMN.ParallelGateway, BPMN.InclusiveGateway}:
                out_edges = self.__get_gateway_out_arcs(node)
                in_edges = self.__get_gateway_inc_arcs(node)

                direction = "Converging" if len(in_edges) > len(out_edges) else "Diverging"
                node.set_gatewayDirection(direction)

    def __get_gateway_out_arcs(self, node : Union[BPMN.ExclusiveGateway, BPMN.InclusiveGateway, BPMN.ParallelGateway]):
        set = []
        outgoing = node.get_out_arcs()
        for out in outgoing:
            set.append("id" + str(out.get_id()))
        return set

    def __get_gateway_inc_arcs(self, node : Union[BPMN.ExclusiveGateway, BPMN.InclusiveGateway, BPMN.ParallelGateway]):
        set = []
        incoming = node.get_in_arcs()
        for inc in incoming:
            set.append("id" + str(inc.get_id()))
        return set

    def get_bpmn(self):
        if self.bpmn is None:
            self.convert_to_bpmn()
        return self.bpmn

    def write_bpmn(self, iter : int = None, extension : str = '.bpmn'):
        filename = f"{iter}-BPMN-{self.sequence}-{self.choice}-{self.parallel}{extension}".replace('None-', '')
        pm4py.write_bpmn(self.bpmn, os.path.join("BPMN", filename))
        self.bpmn_file = filename

    def write_processtree(self, iter : int = None, extension : str = '.ptml'):
        filename = f"{iter}-PT-{self.sequence}-{self.choice}-{self.parallel}{extension}".replace('None-', '')
        pm4py.write_process_tree(self.process_tree, os.path.join("ProcessTree", filename))
        self.pt_file = filename

    def calc_simulation_length(self):
        min, mode, max = self.__tree_size
        acts = self.get_activity_count()
        range = (15, 90)

        def normalise(range : Tuple[int, int], obs : int):
            min, max = range
            if obs < min:
                return 0
            elif obs <= max:
                return (obs - min) / (max - min)
            else:
                return 1

        norm = normalise((min, max), acts)

        def sample_norm(range: Tuple[int, int], val: float):
            min, max = range
            return round(val * (max - min) + min)

        return sample_norm(range, norm) + random.randint(-5, 5)