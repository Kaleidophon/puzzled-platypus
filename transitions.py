# -*- coding: utf-8 -*-
"""
Module defining the transition graph.
"""

# CONST
QUANTITY_SPACE_INFLOW = ("0", "+")
QUANTITY_SPACE_OUTFLOW = QUANTITY_SPACE_VOLUME = ("0", "+", "max")
QUANTITY_SPACES = {
    "inflow": QUANTITY_SPACE_INFLOW,
    "outflow": QUANTITY_SPACE_OUTFLOW,
    "volume": QUANTITY_SPACE_VOLUME
}


class Quantity:
    """
    Class modeling a quantity of a inflow, outflow or volume.
    """
    class Quantifiable:
        """
        Class to model a magnitude or a derivative.
        """
        def __init__(self, value, quantity_space):
            self.value = value
            self.quantity_space = quantity_space
            self.space_ceil = len(quantity_space) - 1
            self.value_index = quantity_space.index(value)

        def __add__(self, other):
            assert other == 1, "You can only add one to a quantifiable."

            if self.value_index != self.space_ceil:
                self.value_index += 1
                self.value = self.quantity_space[self.value_index]

            return self

        def __iadd__(self, other):
            return self.__add__(other)

        def __sub__(self, other):
            assert other == 1, "You can only subtract one to a quantifiable."
            if self.value_index != 0:
                self.value_index -= 1
                self.value = self.quantity_space[self.value_index]

            return self

        def __isub__(self, other):
            return self.__sub__(other)

        def __str__(self):
            return self.value

    def __init__(self, model, magnitude="0", derivative="0"):
        assert model in QUANTITY_SPACES.keys()
        self.quantity_space = QUANTITY_SPACES[model]
        assert magnitude in self.quantity_space
        assert derivative in self.quantity_space

        # Wrap magnitude and derivative in Quantifiables for neat addition / subtraction functionalities
        self.magnitude = self.Quantifiable(value=magnitude, quantity_space=self.quantity_space)
        self.derivative = self.Quantifiable(value=derivative, quantity_space=self.quantity_space)


class State:
    """
    Class modeling the state in a transition graph.
    """
    def __init__(self, *quantities):
        assert all([type(quantity) == Quantity for quantity in quantities])
        self.inflow_quantity, self.volume_quantity, self.outflow_quantity = quantities


class TransitionGraph:
    """
    Class defining the transition graph modeling the states of containers and the transitions between them.
    """
    def __init__(self, states, transitions):
        self.states = states
        self.transitions = transitions


def check_transition_graph_consistency(transition_graph):
    # TODO: Implement
    pass


if __name__ == "__main__":
    outflow = Quantity("outflow", derivative="max")
    print("Magnitude", outflow.magnitude)
    outflow.magnitude += 1
    print("Magnitude", outflow.magnitude)
    outflow.magnitude += 1
    print("Magnitude", outflow.magnitude)
    outflow.magnitude += 1s
    print("Magnitude", outflow.magnitude)
    print("Derivative", outflow.derivative)
    outflow.derivative -= 1
    print("Derivative", outflow.derivative)
    outflow.derivative -= 1
    print("Derivative", outflow.derivative)
    outflow.derivative = outflow.derivative - 1
    print("Derivative", outflow.derivative)
