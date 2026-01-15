from tool_chain.state import State
from retrieval_strategies.retrieval import DataRetriever
from retrieval_strategies.config import RAGConfig

class RetrievalNode:
    def __init__(self, config):
        self.data_retriever = DataRetriever(config)

    def retrieve_rules(self, state: State, top_k=3) -> dict:
        results = self.data_retriever.search_rules(state["feature"], top_k=top_k)
        return {"response": state["response"] + "已经执行retrieval_node","rule": results}