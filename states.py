# -*- coding: utf-8 -*-
"""
Module defining the state graph.
"""

# STD
import copy

from quantities import DiscontinuityException

# CONST
QUANTITY_RELATIONSHIPS = {
    "I+",
    "I-",
    "P+",
    "P-",
    "VC_max",
    "VC_0",
    "C+",       # A positive derivative will increment the magnitude of the same quantity
    "C-",       # A negative derivative will decrement the magnitude of the same quantity
    "A+",       # Open tap
    "A-"        # Close tap
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

    def envision(self):
        if not (self.states or self.transitions):
            self.states, self.transitions = self._envision()
        return self.states, self.transitions

    def _envision(self):
        states = {}
        transitions = {}
        state_stack = [self.initial_state]
        discontinuities = 0

        while len(state_stack) != 0:
            current_state = state_stack.pop(0)
            branches = current_state.apply_rules(self.rules)
            branches = [branch for branch in branches if branch is not None]

            for rule, new_state in branches:
                transitions[(current_state.readable_id, rule)] = new_state
                print("{} --({})--> {}".format(current_state.readable_id, rule, new_state.readable_id))
                if new_state.readable_id not in states:
                    states[new_state.readable_id] = new_state
                    state_stack.append(new_state)

            discontinuities += current_state.discontinuity_counter

        print("\n{} state(s) and {} transitions detected.".format(len(states), len(transitions)))
        print("{} state(s) were prohibited due to discontinuities.".format(discontinuities))

        return states, transitions

    @property
    def edges(self):
        states, _ = self.envision()
        return states

    @property
    def nodes(self):
        self.envision()
        _, transitions = self.envision()
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
    discontinuity_counter = 0

    def __init__(self, **entities):
        self.entity_names = entities.keys()
        self.entities = list(entities.values())
        vars(self).update(entities)

    def __repr__(self):
        return "<State: {}>".format(self.readable_id)

    @property
    def readable_id(self):
        return "|".join(
            [
                ";".join(
                    [
                        "{} {}".format(str(quantity.magnitude), str(quantity.derivative))
                        for quantity in entity.quantities
                    ]
                )
                for entity in self.entities
            ]
        )

    def apply_rules(self, rules):
        branches = []

        for rule in rules:
            try:
                branches.append(rule.apply(self))
            except DiscontinuityException:
                self.discontinuity_counter += 1

        return branches

    def __copy__(self):
        return State(**dict(zip(self.entity_names, [copy.copy(entity) for entity in self.entities])))


