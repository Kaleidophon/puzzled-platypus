import abc
import copy

from states import QUANTITY_RELATIONSHIPS


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
        if quantity1.magnitude != "+" and quantity2.derivative != "+":
            new_state = copy.copy(state)
            new_quantity = self.get_quantity(new_state, self.entity_name2, self.quantity_name2)
            new_quantity.derivative += 1
            return self.relation, new_state

        if quantity1.magnitude != "-" and quantity2.derivative != "-":
            new_state = copy.copy(state)
            new_quantity = self.get_quantity(new_state, self.entity_name2, self.quantity_name2)
            new_quantity.derivative -= 1
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