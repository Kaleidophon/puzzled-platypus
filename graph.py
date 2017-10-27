# -*- coding: utf-8 -*-
"""
Module defining our project's causal graph.
"""

# PROJECT
from quantities import Quantity
from entities import Tap, Container, Drain
from states import StateGraph, State
from relationships import (
    PositiveConsequence,
    NegativeConsequence,
    PositiveInfluence,
    NegativeInfluence,
    PositiveProportion,
    VCmax,
    VCzero
)


def init_minimum_viable_state_graph(verbosity=0):
    # Construct tap
    inflow = Quantity("inflow", derivative="+")
    tap = Tap(inflow=inflow)

    # Construct container
    volume = Quantity("volume")
    container = Container(volume=volume)

    # Construct drain
    outflow = Quantity("outflow")
    drain = Drain(outflow=outflow)

    # Set up relationships
    inter_state = [
        PositiveInfluence(source="tap.inflow", target="container.volume"),
        NegativeInfluence(source="drain.outflow", target="container.volume"),
        PositiveProportion(source="container.volume", target="drain.outflow")
    ]
    intra_state = [
        PositiveConsequence(target="tap.inflow"),
        NegativeConsequence(target="tap.inflow"),
        PositiveConsequence(target="container.volume"),
        NegativeConsequence(target="container.volume"),
        PositiveConsequence(target="drain.outflow"),
        NegativeConsequence(target="drain.outflow"),
        VCmax(source="container.volume", target="drain.outflow"),
        VCzero(source="container.volume", target="drain.outflow")
    ]

    # Create initial state
    init_state = State(tap=tap, container=container, drain=drain)

    # Create state graph
    state_graph = StateGraph(
        initial_state=init_state, inter_state=inter_state, intra_state=intra_state, verbosity=verbosity
    )
    return state_graph


def init_extra_points_state_graph(verbosity=0):
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
    inter_state = [
        PositiveInfluence(source="tap.inflow", target="container.volume"),
        NegativeInfluence(source="drain.outflow", target="container.volume"),
        PositiveProportion(source="container.volume", target="container.height"),
        PositiveProportion(source="container.height", target="container.pressure"),
        PositiveProportion(source="container.pressure", target="drain.outflow"),
    ]
    intra_state = [
        PositiveConsequence(target="tap.inflow"),
        NegativeConsequence(target="tap.inflow"),
        PositiveConsequence(target="container.volume"),
        NegativeConsequence(target="container.volume"),
        PositiveConsequence(target="container.height"),
        NegativeConsequence(target="container.height"),
        PositiveConsequence(target="container.pressure"),
        NegativeConsequence(target="container.pressure"),
        PositiveConsequence(target="drain.outflow"),
        NegativeConsequence(target="drain.outflow"),
        VCmax(source="container.volume", target="container.height"),
        VCzero(source="container.volume", target="container.height"),
        VCmax(source="container.height", target="container.pressure"),
        VCzero(source="container.height", target="container.pressure"),
        VCmax(source="container.pressure", target="drain.outflow"),
        VCzero(source="container.pressure", target="drain.outflow")
    ]

    # Create initial state
    init_state = State(tap=tap, container=container, drain=drain)

    # Create state graph
    state_graph = StateGraph(
        initial_state=init_state, inter_state=inter_state, intra_state=intra_state, verbosity=verbosity
    )
    return state_graph
