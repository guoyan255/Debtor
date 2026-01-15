from tool_chain.state import State
from langgraph.graph import START, StateGraph
from tool_chain.feature_matching import feature_matching
from tool_chain.retrieval_node import RetrievalNode
from tool_chain.risk_score import risk_score
from tool_chain.risk_reporting import risk_reporting
from tool_chain.state import State
from tool_chain.data_loader import data_loader
from retrieval_strategies.config import RAGConfig


class risk_graph:

    def __init__(self):
        self.graph = StateGraph(State)

    def get_graph(self) -> dict:

        config = RAGConfig(collection_name="risk_rules_collection")

        node_data_loader = data_loader()
        node_feature_matching = feature_matching()
        node_retrieval_node = RetrievalNode(config)
        node_risk_score = risk_score()
        node_risk_reporting = risk_reporting()


        self.graph.add_node("data_loader", node_data_loader.load_data)
        self.graph.add_node("feature_matching", node_feature_matching.match_features)
        self.graph.add_node("retrieval_node", node_retrieval_node.retrieve_rules)
        self.graph.add_node("risk_score", node_risk_score.assess_risk)
        self.graph.add_node("risk_reporting", node_risk_reporting.warn_risk)

        self.graph.add_edge(START, "data_loader")
        self.graph.add_edge("data_loader", "feature_matching")
        self.graph.add_edge("feature_matching", "retrieval_node")
        self.graph.add_edge("retrieval_node", "risk_score")
        self.graph.add_edge("risk_score", "risk_reporting")





        return self.graph