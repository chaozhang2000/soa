from typing import Annotated, List, TypedDict
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
import operator

class State(TypedDict):
    execution_order: Annotated[List[str], operator.add]
    error:bool

def node_a(state: State):
    if state["error"] == True:
        raise ValueError("Failure")
    return {"execution_order": ["A"],}
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

checkpointer=InMemorySaver()
graph=graph_builder.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "1"}}
try:
    result = graph.invoke({"error":True},config)
except ValueError as e:
    print(e)

    print("\ncurrent state:")
    print(graph.get_state(config).values)
    print(graph.get_state(config).config)

    print("\nfirst fix:update state")
    graph.update_state(graph.get_state(config).config,{"error":False})
    print(graph.get_state(config).config)
    result = graph.invoke(None,graph.get_state(config).config)
    print("fixed\n")

    print("history:")
    for history_snapshot in list(graph.get_state_history(config)): print(history_snapshot.values)