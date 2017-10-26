# -*- coding: utf-8 -*-
"""
Module defining our project's causal graph.
"""

# PROJECT
from quantities import Quantity
from entities import Tap, Container, Drain
from states import (
    StateGraph,
    State
)
from relationships import PositiveConsequence, NegativeConsequence, PositiveAction, NegativeAction, PositiveInfluence, \
    NegativeInfluence, PositiveProportion, VCmax, VCzero


def main():
    state_graph = init_minimum_viable_state_graph()
    #state_graph = init_extra_points_state_graph()
    state_graph.envision(verbosity=2)


def init_minimum_viable_state_graph():
    # Construct tap
    inflow = Quantity("inflow", derivative="+")
    tap = Tap(inflow=inflow)

    # Construct container
    volume = Quantity("volume")
    container = Container(volume=volume)

    # Construct drain
    outflow = Quantity("outflow")
    drain = Drain(outflow=outflow)

    # Set up rules
    rules = [
        #PositiveAction("tap", "inflow"),
        #NegativeAction("tap", "inflow"),
        PositiveInfluence("tap", "inflow", "container", "volume"),
        NegativeInfluence("drain", "outflow", "container", "volume"),
        PositiveProportion("container", "volume", "drain", "outflow"),
    ]
    consequences = [
        PositiveConsequence("tap", "inflow"),
        NegativeConsequence("tap", "inflow"),
        PositiveConsequence("container", "volume"),
        NegativeConsequence("container", "volume"),
        PositiveConsequence("drain", "outflow"),
        NegativeConsequence("drain", "outflow"),
    ]
    constraints = [
        VCmax("container", "volume", "drain", "outflow"),
        VCzero("container", "volume", "drain", "outflow")
    ]

    # Create initial state
    init_state = State(tap=tap, container=container, drain=drain)

    # Create state graph
    state_graph = StateGraph(initial_state=init_state, rules=rules, consequences=consequences, constraints=constraints)
    return state_graph


def init_extra_points_state_graph():
    # Construct tap
    inflow = Quantity("inflow", derivative="+")
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
        PositiveAction("tap", "inflow"),
        NegativeAction("tap", "inflow"),
        PositiveInfluence("tap", "inflow", "container", "volume"),
        NegativeInfluence("drain", "outflow", "container", "volume"),
        PositiveProportion("container", "volume", "container", "height"),
        PositiveProportion("container", "height", "container", "pressure"),
        PositiveProportion("container", "pressure", "drain", "outflow"),
    ]
    consequences = [
        PositiveConsequence("tap", "inflow"),
        NegativeConsequence("tap", "inflow"),
        PositiveConsequence("container", "volume"),
        NegativeConsequence("container", "volume"),
        PositiveConsequence("container", "height"),
        NegativeConsequence("container", "height"),
        PositiveConsequence("container", "pressure"),
        NegativeConsequence("container", "pressure"),
        PositiveConsequence("drain", "outflow"),
        NegativeConsequence("drain", "outflow"),
    ]
    constraints = [
        VCmax("container", "height", "container", "pressure"),
        VCzero("container", "height", "container", "pressure"),
        VCmax("container", "volume", "container", "height"),
        VCzero("container", "volume", "container", "height"),
        VCmax("container", "pressure", "drain", "outflow"),
        VCzero("container", "pressure", "drain", "outflow")
    ]

    # Create initial state
    init_state = State(tap=tap, container=container, drain=drain)

    # Create state graph
    state_graph = StateGraph(initial_state=init_state, rules=rules, consequences=consequences, constraints=constraints)
    return state_graph

if __name__ == "__main__":
    main()
