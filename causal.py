# -*- coding: utf-8 -*-
"""
Module defining our project's causal graph.
"""

# PROJECT
from quantities import Quantity
from entities import Tap, Container, Drain
from states import StateGraph, State, ValueCorrespondence, PositiveConsequence


def main():
    pass


def build_causal_graph():
    # Construct tap
    inflow = Quantity("inflow")
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
        PositiveConsequence(inflow),
        PositiveConsequence(volume)
    ]

if __name__ == "__main__":
    main()
