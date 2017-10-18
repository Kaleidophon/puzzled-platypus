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
        return [rule.apply(self) for rule in rules]

    def __copy__(self):
        return State(**dict(zip(self.entity_names, [copy.copy(entity) for entity in self.entities])))


class Relationship:

    def __init__(self, entity_name1, quantity_name1, entity_name2, quantity_name2, relation):
        assert relation in QUANTITY_RELATIONSHIPS, "Unknown relationship"
        self.entity1 = entity_name1
        self.entity2 = entity_name2
        self.quantity1 = quantity_name1
        self.quantity2 = quantity_name2
        self.relation = relation

    @abc.abstractmethod
    def apply(self, state):
        pass

    @staticmethod
    def get_quantity(state, entity_name, quantity_name):
        entity = getattr(state, entity_name)
        return getattr(entity, quantity_name)


class Reflexive(Relationship):
    def __init__(self, entity_name, quantity_name, relation):
        self.entity_name = entity_name
        self.quantity_name = quantity_name
        super().__init__(entity_name, quantity_name, entity_name, quantity_name, relation)

    @abc.abstractmethod
    def apply(self, state):
        pass


class PositiveConsequence(Reflexive):
    def __init__(self, entity_name, quantity_name):
        super().__init__(entity_name, quantity_name, "C+")

    def apply(self, state):
        quantity = self.get_quantity(state, self.entity_name, self.quantity_name)
        if quantity.derivative == "+" and not quantity.magnitude.is_max():
            new_state = copy.copy(state)
            new_quantity = self.get_quantity(new_state, self.entity_name, self.quantity_name)
            new_quantity.magnitude += 1
            return self.relation, new_state


class NegativeConsequence(Reflexive):
    def __init__(self, entity_name, quantity_name):
        super().__init__(entity_name, quantity_name, "C-")

    def apply(self, state):
        quantity = self.get_quantity(state, self.entity_name, self.quantity_name)
        if quantity.derivative == "-" and not quantity.magnitude.is_min():
            new_state = copy.copy(state)
            new_quantity = self.get_quantity(new_state, self.entity_name, self.quantity_name)
            new_quantity.magnitude -= 1
            return self.relation, new_state


class PositiveAction(Reflexive):
    def __init__(self, entity_name, quantity_name):
        super().__init__(entity_name, quantity_name, "A+")

    def apply(self, state):
        quantity = self.get_quantity(state, self.entity_name, self.quantity_name)
        if not quantity.derivative.is_max():
            new_state = copy.copy(state)
            new_quantity = self.get_quantity(new_state, self.entity_name, self.quantity_name)
            new_quantity.derivative += 1
            return self.relation, new_state


class NegativeAction(Reflexive):
    def __init__(self, entity_name, quantity_name):
        super().__init__(entity_name, quantity_name, "A-")

    def apply(self, state):
        quantity = self.get_quantity(state, self.entity_name, self.quantity_name)
        if not quantity.derivative.is_min():
            new_state = copy.copy(state)
            new_quantity = self.get_quantity(new_state, self.entity_name, self.quantity_name)
            new_quantity.derivative -= 1
            return self.relation, new_state


class ValueCorrespondence(Relationship):

    def __init__(self, quantity_name1, magnitude1, quantity_name2, magnitude2, constraint="VC_max"):
        super().__init__(quantity_name1, quantity_name2, relation=constraint)
        assert magnitude1 in quantity_name1.quantity_space, "Invalid value for magnitude: {}".format(magnitude1)
        assert magnitude2 in quantity_name2.quantity_space, "Invalid value for magnitude: {}".format(magnitude2)
        self.magnitude1 = magnitude1
        self.magnitude2 = magnitude2

    def check_correspondence(self):
        if self.quantity2.magnitude == self.magnitude2:
            return self.quantity1.magnitude == self.magnitude1
        return False
