# -*- coding: utf-8 -*-
"""
Module defining our project's causal graph.
"""

# PROJECT
from quantities import Quantity
from entities import Tap, Container, Drain
from states import (
    StateGraph,
    State,
    ValueCorrespondence,
    PositiveConsequence,
    NegativeConsequence
)


def main():
    state_graph = init_state_graph()
    state_graph.envision()


def init_state_graph():
    # Construct tap
    inflow = Quantity("inflow", derivative="-", magnitude="+")
    tap = Tap(inflow=inflow)

    # Construct container
    volume = Quantity("volume")
    height = Quantity("height")
    pressure = Quantity("pressure")
    container = Container(volume=volume, height=height, pressure=pressure)

    # Construct drain
    outflow = Quantity("outflow")
    drain = Drain(outflow=outflow)

    # Set up rules
    rules = [
        PositiveConsequence(tap.inflow),
        NegativeConsequence(tap.inflow)
        #PositiveConsequence(volume),
        #PositiveConsequence(height),
        #PositiveConsequence(pressure),
        #PositiveConsequence(outflow)
    ]

    # Create initial state
    init_state = State(tap=tap, container=container, drain=drain)

    # Create state graph
    state_graph = StateGraph(initial_state=init_state, rules=rules)
    return state_graph

if __name__ == "__main__":
    main()
