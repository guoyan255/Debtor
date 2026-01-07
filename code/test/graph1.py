from state import State
from node.node_a import NodeA
from node.node_b import NodeB
from langgraph.graph import START, StateGraph


nodea=NodeA()
nodeb=NodeB()



graph = StateGraph(State)
graph.add_node("node_a", nodea.node_a)
graph.add_node("node_b", nodeb.node_b)
graph.add_edge(START, "node_a")
graph.add_edge("node_a", "node_b")


print(graph.compile().invoke({"text": ""}))