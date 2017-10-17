# -*- coding: utf-8 -*-
"""
Module defining the state graph.
"""

# STD
import abc
import copy

# PROJECT
from quantities import QUANTITY_SPACES, Quantity

# CONST
QUANTITY_RELATIONSHIPS = {
    "I+",
    "I-",
    "P+",
    "P-",
    "VC_max",
    "VC_0",
    "C+",       # A positive derivative will increment the magnitude of the same quantity
    "C-"        # A negative derivative will decrement the magnitude of the same quantity

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
    """
    Class to model a state in the state graph.
    """
    def __init__(self, rules, **entities):
        self.rules = rules
        vars(self).update(entities)

    def apply_rules(self):
        branches = []

        for rule in self.rules:
            branches.append(rule.apply(self))


class Relationship:

    def __init__(self, quantity1, quantity2, relation):
        assert type(quantity1) == Quantity and type(quantity2) == Quantity
        assert relation in QUANTITY_RELATIONSHIPS, "Unknown relationship"
        self.quantity1 = quantity1
        self.quantity2 = quantity2
        self.relation = relation

    @abc.abstractmethod
    def apply(self, state):
        pass


class Consequence(Relationship):
    def __init__(self, quantity, relation):
        super().__init__(quantity, quantity, relation)


class PositiveConsequence(Consequence):
    def __init__(self, quantity):
        super().__init__(quantity, "C+")

    def apply(self, state):
        if self.quantity1.derivative == "+" and not self.quantity1.magnitude.is_max:
            new_state = copy.copy(state)
            new_state.magnitude += 1
            return self.relation, new_state


class ValueCorrespondence(Relationship):

    def __init__(self, quantity1, magnitude1, quantity2, magnitude2, constraint="VC_max"):
        super().__init__(quantity1, quantity2, relation=constraint)
        assert magnitude1 in quantity1.quantity_space, "Invalid value for magnitude: {}".format(magnitude1)
        assert magnitude2 in quantity2.quantity_space, "Invalid value for magnitude: {}".format(magnitude2)
        self.magnitude1 = magnitude1
        self.magnitude2 = magnitude2

    def check_correspondence(self):
        if self.quantity2.magnitude == self.magnitude2:
            return self.quantity1.magnitude == self.magnitude1
        return False


if __name__ == "__main__":
   rules = []
