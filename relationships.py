# -*- coding: utf-8 -*-
"""
Module defining different kinds of relationships.
"""

# STD
import abc
import copy

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


class ConstraintEnforcementException(Exception):
    pass


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
            return new_state


class NegativeConsequence(Reflexive):
    def __init__(self, entity_name, quantity_name):
        super().__init__(entity_name, quantity_name, "C-")

    def apply(self, state):
        quantity = self.get_quantity(state, self.entity_name, self.quantity_name)
        if quantity.derivative == "-" and not quantity.magnitude.is_min():
            new_state = copy.copy(state)
            new_quantity = self.get_quantity(new_state, self.entity_name, self.quantity_name)
            new_quantity.magnitude -= 1
            return new_state


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


class Influence(Relationship):
    def __init__(self, entity_name1, quantity_name1, entity_name2, quantity_name2, relation):
        self.entity_name1 = entity_name1
        self.quantity_name1 = quantity_name1
        self.entity_name2 = entity_name2
        self.quantity_name2 = quantity_name2
        super().__init__(entity_name1, quantity_name1, entity_name2, quantity_name2, relation)

    @abc.abstractmethod
    def apply(self, state):
        pass


class PositiveInfluence(Influence):
    def __init__(self, entity_name1, quantity_name1, entity_name2, quantity_name2):
        super().__init__(entity_name1, quantity_name1, entity_name2, quantity_name2, "I+")

    def apply(self, state):
        quantity1 = self.get_quantity(state, self.entity_name1, self.quantity_name1)
        quantity2 = self.get_quantity(state, self.entity_name2, self.quantity_name2)
        if quantity1.magnitude != "0" and quantity2.derivative != "+":
            new_state = copy.copy(state)
            new_quantity = self.get_quantity(new_state, self.entity_name2, self.quantity_name2)
            new_quantity.derivative += 1
            return self.relation, new_state


class NegativeInfluence(Influence):
    def __init__(self, entity_name1, quantity_name1, entity_name2, quantity_name2):
        super().__init__(entity_name1, quantity_name1, entity_name2, quantity_name2, "I-")

    def apply(self, state):
        quantity1 = self.get_quantity(state, self.entity_name1, self.quantity_name1)
        quantity2 = self.get_quantity(state, self.entity_name2, self.quantity_name2)
        if quantity1.magnitude != "0" and quantity2.derivative != "-":
            new_state = copy.copy(state)
            new_quantity = self.get_quantity(new_state, self.entity_name2, self.quantity_name2)
            new_quantity.derivative -= 1
            return self.relation, new_state


class Proportion(Relationship):
    def __init__(self, entity_name1, quantity_name1, entity_name2, quantity_name2, relation):
        self.entity_name1 = entity_name1
        self.quantity_name1 = quantity_name1
        self.entity_name2 = entity_name2
        self.quantity_name2 = quantity_name2
        super().__init__(entity_name1, quantity_name1, entity_name2, quantity_name2, relation)

    @abc.abstractmethod
    def apply(self, state):
        pass


class PositiveProportion(Proportion):
    def __init__(self, entity_name1, quantity_name1, entity_name2, quantity_name2):
        super().__init__(entity_name1, quantity_name1, entity_name2, quantity_name2, "P+")

    def apply(self, state):
        quantity1 = self.get_quantity(state, self.entity_name1, self.quantity_name1)
        quantity2 = self.get_quantity(state, self.entity_name2, self.quantity_name2)

        if quantity1.derivative == "+" and quantity2.derivative != "+":
            new_state = copy.copy(state)
            new_quantity = self.get_quantity(new_state, self.entity_name2, self.quantity_name2)
            new_quantity.derivative += 1
            return self.relation, new_state

        elif quantity1.derivative == "-" and quantity2.derivative != "-":
            new_state = copy.copy(state)
            new_quantity = self.get_quantity(new_state, self.entity_name2, self.quantity_name2)
            new_quantity.derivative -= 1
            return self.relation, new_state


class ValueCorrespondence(Relationship):
    def __init__(self, entity_name1, quantity_name1, magnitude1, entity_name2, quantity_name2, magnitude2, constraint):
        super().__init__(entity_name1, quantity_name1, entity_name2, quantity_name2, relation=constraint)
        self.entity_name1 = entity_name1
        self.quantity_name1 = quantity_name1
        self.entity_name2 = entity_name2
        self.quantity_name2 = quantity_name2
        self.magnitude1 = magnitude1
        self.magnitude2 = magnitude2

    @abc.abstractmethod
    def apply(self, state):
        pass


class VCmax(ValueCorrespondence):
    def __init__(self, entity_name1, quantity_name1, entity_name2, quantity_name2):
        super().__init__(entity_name1, quantity_name1, "max", entity_name2, quantity_name2, "max", "VC_max")

    def apply(self, state):
        quantity1 = self.get_quantity(state, self.entity_name1, self.quantity_name1)
        quantity2 = self.get_quantity(state, self.entity_name2, self.quantity_name2)

        if quantity1.magnitude != "max" or quantity2.magnitude == "max":
            # raise ConstraintEnforcementException("Enforcing VC max constraint.")
            return True
        return False


class VCzero(ValueCorrespondence):
    def __init__(self, entity_name1, quantity_name1, entity_name2, quantity_name2):
        super().__init__(entity_name1, quantity_name1, "0", entity_name2, quantity_name2, "0", "VC_0")

    def apply(self, state):
        quantity1 = self.get_quantity(state, self.entity_name1, self.quantity_name1)
        quantity2 = self.get_quantity(state, self.entity_name2, self.quantity_name2)

        if quantity1.magnitude != "0" or quantity2.magnitude == "0":
            # raise ConstraintEnforcementException("Enforcing VC zero constraint.")
            return True
        return False
