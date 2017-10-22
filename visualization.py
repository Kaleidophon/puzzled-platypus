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
from graphviz import Digraph

# PROJECT
from graph import init_extra_points_state_graph, init_minimum_viable_state_graph


if __name__ == "__main__":
    dot = Digraph(comment='The Round Table', format="png")
    state_graph = init_minimum_viable_state_graph()
    #state_graph = init_extra_points_state_graph()

    for node_uid, node in state_graph.nodes:
        dot.node(node_uid, node.readable_id, shape="box")

    for start, label, target in state_graph.edges:
        dot.edge(start, target, label=label)

    print(dot.source)

    dot.render('test-output/state_graph.png', view=True)
