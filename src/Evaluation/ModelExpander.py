from typing import Tuple
import logging
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.utils import petri_utils

import copy

from src.Evaluation.Cluster import Cluster
from src.Evaluation.Pattern import Pattern


class ModelExpander:
    def __init__(self, name:str, parent:Tuple[PetriNet, Marking, Marking], patterns:list) -> None:
        self.name = name
        self.parent = copy.deepcopy(parent)
        self.patterns = copy.deepcopy(patterns)
        self.ExpandedNet = None

        self.abstractpatterns = 0

    def lpm(self) -> None:
        if self.patterns is not None and len(self.patterns) > 0:
            net, im, fm = self.parent

            for pattern in self.patterns:
                name = pattern.name.replace("LPM", "LPM ")
                pattern_net, pattern_im, pattern_fm = pattern.net

                # Look up the transition for this pattern in the parent net. Track the amount of patterns replaced.
                t_to_replace = ModelExpander.get_transition_by_label(net, name)

                if t_to_replace is not None:
                    net, im, fm = ModelExpander.replace_transition(net, im, fm, t_to_replace, pattern_net, name)
                    self.abstractpatterns += 1

            self.ExpandedNet = net, im , fm

    def cobpam(self) -> None:
        if self.patterns is not None and len(self.patterns) > 0:
            pass

        # Don't forget to count the amount of patterns we are replacing in self.abstractpatterns

    def massimiliano(self) -> None:
        if self.patterns is not None and len(self.patterns) > 0:
            # logging.log(logging.DEBUG, f"{self.name}: Expanding for Massimiliano's Clusters.")
            net, im, fm = self.parent
            for cluster in self.patterns:            
                index = cluster.index
                cluster_net, cluster_im, cluster_fm = cluster.get_petri()
                suffix = "Massimiliano_Cluster" + str(index)

                # Look up the transition for this cluster in the parent net. Track the amount of patterns replaced.
                t_to_replace = ModelExpander.get_transition_by_index(net, index)

                if t_to_replace is not None:
                    net, im, fm = ModelExpander.replace_transition(net, im, fm, t_to_replace, cluster_net, suffix)
                    self.abstractpatterns += 1

            self.ExpandedNet = net, im , fm
            # logging.log(logging.DEBUG, f"{self.name}: Parent Net expansion for MASSIMILIANO completed.")

        else:
            # logging.log(logging.DEBUG, f"{self.name}: No clusters found. Aborting")
            self.ExpandedNet = None

    def get_expanded_net(self) -> Tuple[PetriNet, Marking, Marking]:
        return self.ExpandedNet

    def get_num_abstracted_patterns(self) -> int:
        return self.abstractpatterns

    def get_num_patterns(self) -> int:
        return len(self.patterns)

    def reset(self) -> None:
        self.ExpandedNet = None
        self.abstractpatterns = 0        
    
    @staticmethod
    def get_transition_by_index(net:PetriNet, index:int) -> PetriNet.Transition:
        for t in net.transitions:
            if t.label is None:
                continue

            name = t.label
            for letter in "abcdefghijklmnopqrstuvwxyz":
                name = name.replace(letter, "")
            if name == str(index):
                return t
        return None

    @staticmethod
    def get_transition_by_label(net:PetriNet, label:str) -> PetriNet.Transition:
        for t in net.transitions:
            if t.label == label:
                return t
        return None

    @staticmethod
    def get_place_by_name(net:PetriNet, place_name:str) -> PetriNet.Place:
        for p in net.places:
            if p.name == place_name:
                return p
        return None

    @staticmethod
    def replace_transition(net:PetriNet, im:Marking, fm:Marking, transition:PetriNet.Transition, pattern:PetriNet, suffix:str) -> Tuple[PetriNet, Marking, Marking]:

        # Create the hidden source and sinks for the replacement pattern: connect to main net through them
        hidden_source = PetriNet.Transition(suffix + "_Hidden_Source")
        net.transitions.add(hidden_source)

        in_arcs = transition.in_arcs
        for arc in in_arcs:
            petri_utils.add_arc_from_to(arc.source, hidden_source, net)
        
        hidden_sink = PetriNet.Transition(suffix + "_Hidden_Sink")
        net.transitions.add(hidden_sink)

        out_arcs = transition.out_arcs
        for arc in out_arcs:
            petri_utils.add_arc_from_to(hidden_sink, arc.target, net)

        # Recreate the pattern inside the main net
        for arc in pattern.arcs:
            # if the source of the arc is a place, check if the place exists. Create it if not.
            if type(arc.source) == PetriNet.Place:
                source = ModelExpander.get_place_by_name(net, arc.source.name + "_" + suffix)
                # If the place is None, then create it and add it to the parent net
                if source is None:
                    source = PetriNet.Place(arc.source.name + "_" + suffix)
                    net.places.add(source)
                    
                    # Is the source place the source of the pattern? Then link it to the hidden source transition
                    if len(arc.source.in_arcs) == 0:
                        petri_utils.add_arc_from_to(hidden_source, source, net)

                # If the target (a transition) is None, then create it and add it to the parent net
                target = petri_utils.get_transition_by_name(net, arc.target.name + "_" + suffix)
                if target is None:
                    target = PetriNet.Transition(arc.target.name + "_" + suffix, arc.target.label)
                    net.transitions.add(target)

            # if the source of the arc is a transition, check if the transition exists. Create it if not.
            elif type(arc.source) == PetriNet.Transition:
                source = petri_utils.get_transition_by_name(net, arc.source.name + "_" + suffix)
                # If the transition is None, then create it and add it to the parent net
                if source is None:
                    source = PetriNet.Transition(arc.source.name + "_" + suffix, arc.source.label)
                    net.transitions.add(source)

                # If the target (a place) is None, then create it and add it to the parent net
                target = ModelExpander.get_place_by_name(net, arc.target.name + "_" + suffix)
                if target is None:
                    target = PetriNet.Place(arc.target.name + "_" + suffix)
                    net.places.add(target)

                    # Is the target place the sink of the pattern? Then link it to the hidden sink transition
                    if len(arc.target.out_arcs) == 0:
                        petri_utils.add_arc_from_to(target, hidden_sink, net)

            # Now that the source and target are created / identified, create the arc between the recreation of the pattern.
            petri_utils.add_arc_from_to(source, target, net)

        # Having rebuilt the pattern and connected it, we can now remove the original transition
        petri_utils.remove_transition(net, transition)

        return net, im, fm