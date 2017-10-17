# -*- coding: utf-8 -*-
"""
Module defining the state graph.
"""

# PROJECT
from quantities import Quantity, FrozenQuantity


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

class Rule:
    def __init__(self, entity1, entity2):
        #assert type(entity1) == Entity and type(entity2) == Entity
        self.entity1 = entity1
        self.entity2 = entity2

    def apply(self):
        """
        Check whether a rule applies to the current circumstances.
        """
        pass



class VC(Rule):
    def apply(self):
        if self.entity2.volume.magnitude == "max":
            if self.entity1.volume.magnitude == "max":
                return True
            else:
                return False
        return False



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


if __name__ == "__main__":
    container = Container(
        dependencies=[],
        volume=Quantity(model="outflow", magnitude="+")
    )
    drain = Drain(
        dependencies=[],
        volume=Quantity(model="outflow", magnitude="max")
    )
    vc = VC(container, drain)
    print(vc.apply())
    #print(container.pressure)


