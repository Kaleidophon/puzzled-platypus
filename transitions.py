# -*- coding: utf-8 -*-
"""
Module defining the transition graph.
"""

# CONST
from quantities import Quantity, FrozenQuantity

class State:
    """
    Class modeling the state in a transition graph.
    """
    def __init__(self, *quantities):
        assert all([type(quantity) == Quantity for quantity in quantities]), \
            "All quantities of a state have to be of type Quantity: {} found".format(
                " ,".join([str(type(arg)) for arg in quantities if type(arg) != Quantity])
            )
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
    print("Magnitude", outflow.magnitude)
    outflow.magnitude += 1
    print("Magnitude", outflow.magnitude)
    outflow.magnitude += 1
    print("Magnitude", outflow.magnitude)
    print("Derivative", outflow.derivative)
    outflow.derivative -= 1
    print("Derivative", outflow.derivative)
    outflow.derivative -= 1
    print("Derivative", outflow.derivative)
    outflow.derivative = outflow.derivative - 1
    print("Derivative", outflow.derivative)
