from graphviz import Digraph
#Add the path of graphviz to render the graph
import os
os.environ["PATH"] += os.pathsep + 'C:/Program Files/graphviz-2.38/bin'

dot = Digraph(comment='The Round Table')
#add nodes
dot.node('I', 'Inflow')
dot.node('V', 'Volume')
dot.node('O', 'Outflow')
#add edges
dot.edge('I', 'V', label='I+')
dot.edge('V', 'O', label='P+')
dot.edge('O', 'V', label="I-")
#print the graph
print(dot.source)
#view graph
dot.render('test-output/round-table.gv', view=True)