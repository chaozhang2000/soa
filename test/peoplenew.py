from typing import Annotated, List, TypedDict
from langgraph.graph import StateGraph, START, END
import operator
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    execution_order: Annotated[List[str], operator.add]

def node_a(state: State):return {"execution_order": ["A"],}
def node_people(state: State):
    decision = interrupt("approve?")
    if decision == "approve":
        return Command(goto="B", update={"execution_order":["approve"]})
    else:
        return Command(goto="C", update={"execution_order":["reject"]})
def node_b(state: State):return {"execution_order": ["B"]}
def node_c(state: State):return {"execution_order": ["C"]}

# 1. 构建状态图
graph_builder = StateGraph(State)
graph_builder.add_node("A", node_a)
graph_builder.add_node("B", node_b)
graph_builder.add_node("C", node_c)
graph_builder.add_node("People", node_people)
graph_builder.add_edge(START, "A")
graph_builder.add_edge("A","People")
graph_builder.add_edge("B", END)
graph_builder.add_edge("C", END)

checkpointer=InMemorySaver()
graph=graph_builder.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "1"}}
result = graph.invoke({},config=config)
print(result)
final_result = graph.invoke(Command(resume="approve"), config=config)
print(final_result)