from typing import Annotated, List, TypedDict
from langgraph.graph import StateGraph, START, END
import operator

class State(TypedDict):
    execution_order: Annotated[List[str], operator.add]

def node_a(state: State):return {"execution_order": ["A"],}
def node_b(state: State):return {"execution_order": ["B"],}
def node_c(state: State):return {"execution_order": ["C"],}

# 1. 构建状态图
graph_builder = StateGraph(State)
graph_builder.add_node("A", node_a)
graph_builder.add_node("B", node_b)
graph_builder.add_node("C", node_c)
graph_builder.add_edge(START, "A")
graph_builder.add_edge("A", "B")
graph_builder.add_edge("A", "C")
graph_builder.add_edge("B", END)
graph_builder.add_edge("C", END)

graph=graph_builder.compile()
result = graph.invoke({})
print(result)