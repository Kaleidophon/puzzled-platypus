# -*- coding: utf-8 -*-
"""
Module defining ways to visalize the state graph and the causal model.
"""

# STD
import argparse

# EXT
from graphviz import Digraph


def _init_argparser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '--graph', "-g", choices=["minimal", "extra"],
        help="Type of state graph that is going to be displayed."
    )
    argparser.add_argument(
        "--verbosity", "-v", type=int, choices=range(4), default=1,
        help="Verbosity of state graph algorithm"
    )
    return argparser


def visualize_state_graph(state_graph, graph_type):
    dot = Digraph(comment='State graph', format="png")
    dot.attr(label="State Graph", fontsize="20")

    for node_uid, node in state_graph.nodes:
        entries = node.readable_id.split("|")
        values = entries[0].split()
        node_data = "I(M:" + values[0] + ", D:" + values[1] + ")\n"
        entry = entries[1].split(";")
        if graph_type == "minimal":
            values = entry[0].split()
            node_data += "V(M:" + values[0] + ", D:" + values[1] + ")\n"
            values = entries[2].split()
            node_data += "O(M:" + values[0] + ", D:" + values[1] + ")\n"
        else:
            values = entry[0].split()
            node_data += "V(M:" + values[0] + ", D:" + values[1] + ")\n"
            values = entry[1].split()
            node_data += "H(M:" + values[0] + ", D:" + values[1] + ")\n"
            values = entry[2].split()
            node_data += "P(M:" + values[0] + ", D:" + values[1] + ")\n"
            values = entries[2].split()
            node_data += "O(M:" + values[0] + ", D:" + values[1] + ")\n"

        dot.node(node_uid, node_data, shape="box", fontsize="10", style="filled", fillcolor="#DDDDDD")

    for start, target in state_graph.edges:
        dot.edge(start.uid, target.uid)

    dot.render('img/{}_states'.format(graph_type), view=True)


def visualize_causal_model(state_graph, graph_type, super_entity="Super"):
    dot = Digraph(
        comment='Causal model', format="png", graph_attr={"layout": "neato", "nodesep": "0.5", "ranksep": "0.5"}
    )
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


class StateGraphPrintingMixin:
    """
    Mixin that provides functions to print the transition and state table of a state graph.
    """
    def _print_transition_table(self, transitions):
        # Not beautiful but still in the scope of this project
        if len(self.initial_state.container.quantities) == 3:
            print("\n{pad} Transitions found {pad}\n".format(pad="#" * 39))
            print(
                "\n{tspace}{tap:<4} | {cspace}{container:<16} | {drain} {relationship} {tap:>5}{tspace} | "
                "{container:>16}{cspace} | {drain}".format(
                    tap="tap", container="container", drain="drain", relationship=" "*12,
                    tspace=" "*2, cspace=" "*8
                )
            )
            print("{}+{}+{}{}{}+{}+{}".format("-"*7, "-"*26, "-"*7, " "*14, "-"*7, "-"*26, "-"*6))

            for start in transitions:
                for end in transitions[start]:
                    print("{start} {pad}---->{pad} {end}".format(
                        start=start.readable_id, end=end.readable_id, pad=" "*4
                    ))

        if len(self.initial_state.container.quantities) == 1:
            print("\n{pad} Transitions found {pad}\n".format(pad="#" * 22))
            print(
                "\n{tspace}{tap:<4} | {cspace}{container} | {drain} {relationship} {tap:>7}{tspace} | "
                "{container}{cspace} | {drain}".format(
                    tap="tap", container="cont.", drain="drain", relationship=" "*12,
                    tspace=" "*2, cspace=" "*1
                )
            )
            print("{}+{}+{}{}{}+{}+{}".format("-" * 7, "-" * 8, "-" * 7, " " * 14, "-" * 9, "-" * 8, "-" * 6))

            for start in transitions:
                for end in transitions[start]:
                    print("{start} {pad}---->{pad} {end}".format(
                        start=start.readable_id, end=end.readable_id, pad=" "*5
                    ))

    def _print_state_table(self, states):
        # Not beautiful but still in the scope of this project
        if len(self.initial_state.container.quantities) == 3:
            print("\n{pad} States found {pad}\n".format(pad="#"*14))
            print("{tspace}{tap:<4} | {cspace}{container:<16} | {drain}".format(
                    tap="tap", container="container", drain="drain", tspace=" "*2, cspace=" "*8
                )
            )
            print("{}+{}+{}".format("-"*7, "-"*26, "-"*7))

        if len(self.initial_state.container.quantities) == 1:
            print("\n{pad} States found {pad}\n".format(pad="#" * 5))
            print("{tspace}{tap:<4} | {cspace}{container} | {drain}".format(
                tap="tap", container="cont.", drain="drain", tspace=" " * 2, cspace=" " * 1
                )
            )
            print("{}+{}+{}".format("-" * 7, "-" * 8, "-" * 7))

        for state in states.values():
            print(state.readable_id)

if __name__ == "__main__":
    from graph import init_extra_points_state_graph, init_minimum_viable_state_graph
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

