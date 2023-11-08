from typing import Tuple
from pm4py.objects.petri_net.obj import PetriNet, Marking

class PetriNetCounter:
    def __init__(self, net : Tuple[PetriNet, Marking, Marking]) -> None:
        self.petri = net[0]
        self.im = net[1]
        self.fm = net[2]

    def get_petri_size(self, include_empty = False):
        if include_empty:
            return len(self.petri.transitions)

        else:
            count = 0
            for t in self.petri.transitions:
                if t.label is not None:
                    count += 1
            return count