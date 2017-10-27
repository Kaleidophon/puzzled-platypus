# -*- coding: utf-8 -*-
"""
Module defining ways to visalize the state graph and the causal model.
"""

# STD
import argparse

# EXT
from graphviz import Digraph

# PROJECT
from graph import init_extra_points_state_graph, init_minimum_viable_state_graph


def _init_argparser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '--graph', "-g", choices=["minimal", "extra"],
        help="Type of state graph that is going to be displayed."
    )
    argparser.add_argument(
        "--verbosity", "-v", choices=range(2), default=1,
        help="Verbosity of state graph algorithm"
    )
    return argparser


def visualize_state_graph(state_graph, graph_type):
    dot = Digraph(comment='State graph', format="png")

    for node_uid, node in state_graph.nodes:
        dot.node(node_uid, node.readable_id.replace(" | ", "\n"), shape="box")

    for start, target in state_graph.edges:
        dot.edge(start, target)

    dot.render('img/{}_states'.format(graph_type), view=True)


def visualize_causal_model(state_graph, graph_type, super_entity="Super"):
    dot = Digraph(comment='Causal model', format="png", graph_attr={"layout": "neato", "nodesep": "0.5", "ranksep": "0.5"})

    entities = state_graph.entities

    # Visualize entities
    dot.node(
        super_entity, super_entity,
        shape="box", fillcolor="#edd29a#edd29a", style="filled"
    )

    for entity in entities:
        entity_name = type(entity).__name__
        dot.node(
            entity_name, entity_name,
            shape="box", fillcolor="#edd29a#edd29a", style="filled"
        )
        dot.edge(entity_name, super_entity, label="part of", fontsize="10", len="1.5")

        # Visualize quantities
        for quantity in entity.quantities:
            quantity_name = entity_name.lower() + "." + quantity.model
            dot.node(
                quantity_name,
                "{}\nM: {}  d: {}".format(quantity.model, quantity.magnitude, quantity.derivative),
                shape="circle", fillcolor="#b3caef", style="filled", width="0.75", fontsize="10"
            )
            dot.edge(entity_name, quantity_name, len="1.5")

    # Visualize dependencies
    for dependency in state_graph.rules:
        start = dependency.entity_name1 + "." + dependency.quantity_name1
        end = dependency.entity_name2 + "." + dependency.quantity_name2
        dot.edge(start, end, label=dependency.relation, len="1.5")

    # Visualize value correspondences
    # TODO [DU 24.10.17]

    dot.render('img/{}_causal'.format(graph_type), view=True)

if __name__ == "__main__":
    argparser = _init_argparser()
    args = argparser.parse_args()
    print(args, "\n")

    state_graph = None

    if args.graph is None or args.graph == "minimal":
        args.graph = "minimal"
        state_graph = init_minimum_viable_state_graph(args.verbosity)
    elif args.graph == "extra":
        state_graph = init_extra_points_state_graph(args.verbosity)

    visualize_state_graph(state_graph, graph_type=args.graph)

