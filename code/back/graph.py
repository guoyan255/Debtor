from tool_chain.state import State
from tool_chain.test1 import NodeA
from tool_chain.test2 import test2
from langgraph.graph import START, StateGraph


nodea=NodeA()
nodeb=test2()



graph = StateGraph(State)
graph.add_node("node_a", nodea.node_a)
graph.add_node("node_b", nodeb.test)
graph.add_edge(START, "node_a")
graph.add_edge("node_a", "node_b")


print(graph.compile().invoke({"text": "1"}))