from state import State


class NodeB:
    def node_b(self, state: State) -> dict:
        return {"text": state["text"] + "b"}