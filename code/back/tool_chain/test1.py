from tool_chain.state import State


class NodeA:

    def node_a(self, state: State) -> dict:
        return {"text": state["text"] + "a"}