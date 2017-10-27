from graphviz import Digraph
#Add the path of graphviz to render the graph
import os
os.environ["PATH"] += os.pathsep + 'C:/Program Files/graphviz-2.38/bin'

dot = Digraph(comment='The Causal Model')
dot.graph_attr['rankdir'] = 'LR'
#add nodes
dot.node('I', 'Inflow')
dot.node('V', 'Volume')
dot.node('H', 'Height')
dot.node('P', 'Pressure')
dot.node('O', 'Outflow')
dot.node('IV', "Ipos", shape='circle', width='0.05')
#add edges
dot.edge('I', 'V', label='I+', color='black')
dot.edge('I', 'IV', len='0.5')
dot.edge('IV', 'V', len='0.5')
dot.edge('V', 'H', label='P+')
dot.edge('H', 'P', label='P+')
dot.edge('P', 'O', label='P+')
dot.edge('O', 'V', label="I-")
#print the graph
print(dot.source)
#view graph
dot.render('test-output/round-table.gv', view=True)