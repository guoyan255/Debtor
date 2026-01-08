from tool_chain.state import State
from tool_chain.test1 import NodeA
from tool_chain.test2 import test2
from langgraph.graph import START, StateGraph



class Graph:

    def __init__(self):
        self.graph = StateGraph(State)


    def get_graph(self):
        nodea=NodeA()
        nodeb=test2()

        self.graph.add_node("node_a", nodea.node_a)
        self.graph.add_node("node_b", nodeb.test)
        self.graph.add_edge(START, "node_a")
        self.graph.add_edge("node_a", "node_b")


        return self.graph

