# from graphviz import Digraph
# #Add the path of graphviz to render the graph
# import os
# os.environ["PATH"] += os.pathsep + 'C:/Program Files/graphviz-2.38/bin'
#
# dot = Digraph(comment='The Round Table')
# #add nodes
# dot.node('I', 'Inflow')
# dot.node('V', 'Volume')
# dot.node('O', 'Outflow')
# #add edges
# dot.edge('I', 'V', label='I+')
# dot.edge('V', 'O', label='P+')
# dot.edge('O', 'V', label="I-")
# #print the graph
# print(dot.source)
# #view graph
# dot.render('test-output/round-table.gv', view=True)

# EXT
import networkx as nx
import matplotlib.pyplot as plt

# PROJECT
from graph import init_extra_points_state_graph, init_minimum_viable_state_graph


if __name__ == "__main__":
    graph = nx.DiGraph()
    state_graph = init_minimum_viable_state_graph()

    for node in state_graph.nodes:
        graph.add_node(node)

    for start, label, end in state_graph.edges:
        graph.add_edge(start, end)

    pos = nx.random_layout(graph)
    nx.draw(graph, pos)

    # show graph
    plt.show()
