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
}


class Relationship:

    def __init__(self, source, target, name):
        assert name in QUANTITY_RELATIONSHIPS, "Unknown relationship"
        self.source_entity_name, self.source_quantity_name = source.split(".")
        self.target_entity_name, self.target_quantity_name = target.split(".")
        self.name = name

    @abc.abstractmethod
    def apply(self, state):
        pass

    def source_quantity(self, state):
        return self.get_quantity(state, self.source_entity_name, self.source_quantity_name)

    def target_quantity(self, state):
        return self.get_quantity(state, self.target_entity_name, self.target_quantity_name)

    @staticmethod
    def get_quantity(state, entity_name, quantity_name):
        entity = getattr(state, entity_name)
        return getattr(entity, quantity_name)


class Reflexive(Relationship):
    def __init__(self, target, name):
        self.entity_name, self.quantity_name = target.split(".")
        super().__init__(source=target, target=target, name=name)

    def quantity(self, state):
        return super().source_quantity(state)

    @abc.abstractmethod
    def apply(self, state):
        pass


class Consequence(Reflexive):
    @abc.abstractmethod
    def apply(self, state):
        pass


class PositiveConsequence(Consequence):
    def __init__(self, target):
        super().__init__(target, "C+")

    def apply(self, state):
        quantity = self.quantity(state)

        if quantity.derivative == "+" and not quantity.magnitude.is_max():
            quantity.magnitude += 1

        return state


class NegativeConsequence(Consequence):
    def __init__(self, target):
        super().__init__(target, "C-")

    def apply(self, state):
        quantity = self.quantity(state)

        if quantity.derivative == "-" and not quantity.magnitude.is_min():
            quantity.magnitude -= 1

        return state


class PositiveInfluence(Relationship):
    def __init__(self, source, target):
        super().__init__(source, target, name="I+")

    def apply(self, state):
        source_quantity = self.source_quantity(state)
        target_quantity = self.target_quantity(state)

        if (source_quantity.magnitude == "+" or source_quantity.magnitude == "max") and \
                not target_quantity.derivative.is_max():

            target_quantity.derivative += (self.name, 1)

        return state


class NegativeInfluence(Relationship):
    def __init__(self, source, target):
        super().__init__(source, target, name="I-")

    def apply(self, state):
        source_quantity = self.source_quantity(state)
        target_quantity = self.target_quantity(state)

        if (source_quantity.magnitude == "+" or source_quantity.magnitude == "max") and \
                not target_quantity.derivative.is_min():
            target_quantity.derivative -= (self.name, 1)

        return state


class PositiveProportion(Relationship):
    def __init__(self, source, target):
        super().__init__(source, target, name="P+")

    def apply(self, state):
        source_quantity = self.source_quantity(state)
        target_quantity = self.target_quantity(state)

        if source_quantity.derivative.delta > 0 and not target_quantity.derivative.is_max():
            target_quantity.derivative += (self.name, 1)

        elif source_quantity.derivative.delta < 0 and not target_quantity.derivative.is_min():
            target_quantity.derivative -= (self.name, 1)

        return state


class ValueCorrespondence(Relationship):
    def __init__(self, source, target, source_magnitude, target_magnitude, name):
        super().__init__(source, target, name)
        self.source_magnitude = source_magnitude
        self.target_magnitude = target_magnitude

    @abc.abstractmethod
    def apply(self, state):
        pass


class VCmax(ValueCorrespondence):
    def __init__(self, source, target):
        super().__init__(source, target, source_magnitude="max", target_magnitude="max", name="VC_max")

    def apply(self, state):
        source_quantity = self.source_quantity(state)
        target_quantity = self.target_quantity(state)

        if source_quantity.magnitude.is_max() and not target_quantity.magnitude.is_max():
            target_quantity.magnitude = "max"

        return state


class VCzero(ValueCorrespondence):
    def __init__(self, source, target):
        super().__init__(source, target, source_magnitude="0", target_magnitude="0", name="VC_0")

    def apply(self, state):
        source_quantity = self.source_quantity(state)
        target_quantity = self.target_quantity(state)

        if source_quantity.magnitude.is_min() and not target_quantity.magnitude.is_min():
            target_quantity.magnitude = "0"

        return state
