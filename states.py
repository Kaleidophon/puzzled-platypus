# -*- coding: utf-8 -*-
"""
Module defining the state graph.
"""

# CONST
from quantities import QUANTITY_SPACES, Quantity, FrozenQuantity

ENTITY_SPACES = {
    "tap": QUANTITY_SPACES,
    "drain": QUANTITY_SPACES,
    "sink": QUANTITY_SPACES
}

QUANTITY_RELATIONSHIPS = {
    "I+": (QUANTITY_SPACES, QUANTITY_SPACES),
    "I-": (QUANTITY_SPACES, QUANTITY_SPACES),
    "P+": (QUANTITY_SPACES, QUANTITY_SPACES),
    "P-": (QUANTITY_SPACES, QUANTITY_SPACES)
}


class StateGraph:
    # has:
    # states
    # transitions

    # Algorithm that generates new states

    # transition rules ("things that create a new state")
    #  - dependencies (I+, I-, ...)
    #  - implications (M:0, D:+ -> M:+, D:+)
    #  - influence (turn up / down tap)
    pass


#class State(Quantity, Relationship):
    # Contains:

    #def __init__(previous_state):
        #self.tap = Quantity("inflow", "0", "0")
        #self.drain = Quantity("outflow", "0", "0")
        #self.sink = Quantity("volume", "0", "0")
        #self.sink = Quantity("pressure", "0", "0")
        #self.sink = Quantity("height", "0", "0")
        # Tap
        # Drain
        # Sink

class Entity:
    entity = None

    # quantities
    def __init__(self, entity):
        assert entity in ENTITY_SPACES.keys(), "Unknown entity"
        self.entity = ENTITY_SPACES[entity]
 
    # dependencies


class Relationship:

    def __init__(self, quantity1, quantity2, relation):
        assert quantity1 in QUANTITY_SPACES.keys(), "Unknown quantity"
        assert quantity2 in QUANTITY_SPACES.keys(), "Unknown quantity"
        assert relation in QUANTITY_RELATIONSHIPS.keys(), "Unknown relationship"
        self.quantity1 = quantity1
        self.quantity2 = quantity2
        self.relation = relation


class ValueCorrespondence(Relationship):

    def __init__(self, quantity1, magnitude1, quantity2, magnitude2):
        super().__init__(quantity1, quantity2, relation="constraint")
        assert magnitude1 in quantity1.quantity_space, "Invalid value for magnitude: {}".format(magnitude1)
        assert magnitude2 in quantity2.quantity_space, "Invalid value for magnitude: {}".format(magnitude2)
        self.magnitude1 = magnitude1
        self.magnitude2 = magnitude2

    def check_correspondence(self):
        if self.quantity2.magnitude == self.magnitude2:
            assert self.quantity1.magnitude == self.magnitude1, "VC Condition failure"


if __name__ == "__main__":


    vc_max = ValueCorrespondence()