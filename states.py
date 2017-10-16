# -*- coding: utf-8 -*-
"""
Module defining the state graph.
"""

# CONST
from quantities import Quantity, FrozenQuantity


class StateGraph:
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
    pass


