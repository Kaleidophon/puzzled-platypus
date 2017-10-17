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
    """
    Class to model a state graph, i.e. a graph with states as nodes and transitions between those same nodes as edges.
    """
    states = None
    transitions = None

    def __init__(self, initial_state, rules):
        self.initial_state = initial_state
        self.rules = rules

    def generate(self):
        if not (self.states or self.transitions):
            self.states, self.transitions = self._generate()
        return self.states, self.transitions

    def _generate(self):
        states = {}
        transitions = {}
        state_stack = [self.initial_state]

        while len(state_stack) != 0:
            current_state = state_stack.pop(0)
            branches = current_state.apply_rules(states)

            for rule, new_state in branches:
                states[new_state.id] = new_state
                transitions[(current_state.id, rule)] = new_state

        return states, transitions

    @property
    def edges(self):
        states, _ = self.generate()
        return states

    @property
    def nodes(self):
        self.generate()
        _, transitions = self.generate()
        return transitions

    # has:
    # states
    # transitions

    # Algorithm that generates new states

    # transition rules ("things that create a new state")
    #  - dependencies (I+, I-, ...)
    #  - implications (M:0, D:+ -> M:+, D:+)
    #  - influence (turn up / down tap)
    pass


class State:
    # Contains:
    # Tap
        # Quantities
            # Inflow
    # Drain
        # Quantities
            # Outflow
    # Sink
        # Quantities
            # Volume
    pass


class Entity:
    # has:
        # quantities
        # dependencies

    def __init__(self, dependencies, **quantities):
        self.dependencies = dependencies
        self.__dict__.update(quantities)
        #vars(self).update(quantities)



class Container(Entity):
    pass


class Drain(Entity):
    pass


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
    container = Container(
        dependencies=[],
        volume=Quantity(model="outflow", magnitude="+")
    )
    drain = Drain(
        dependencies=[],
        volume=Quantity(model="outflow", magnitude="max")
    )

    vc_max = ValueCorrespondence()