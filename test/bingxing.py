import uuid
from typing import Annotated, List, TypedDict
from langgraph.graph import StateGraph, START, END
import time
import operator
from datetime import datetime
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.types import interrupt, Command

class State(TypedDict):
    execution_order: Annotated[List[str], operator.add]
    node_times: Annotated[List[str], operator.add]  # 记录每个节点的执行时间

def format_time():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def node_a(state: State, store: InMemoryStore):
    # 节点A中增加对store的操作
    current_time = format_time()
    store_info = []
    
    # 1. 生成唯一键，可结合线程ID和时间确保唯一性
    thread_id = state.get("thread_id", "unknown")
    key = f"node_a_data_{thread_id}_{current_time}"
    
    # 2. 向store中存储数据
    data_to_store = {
        "node": "A",
        "execution_time": current_time,
        "message": "这是节点A存储的数据",
        "thread_id": thread_id
    }
    store.put(key, data_to_store)
    store_info.append(f"存储数据到键: {key}")
    
    # 3. 从store中读取数据并验证
    retrieved_data = store.get(key)
    if retrieved_data:
        store_info.append(f"成功读取键 {key} 的数据: {retrieved_data['message']}")
    else:
        store_info.append(f"读取键 {key} 失败")
    
    # 模拟节点处理时间
    time.sleep(1)
    
    return {
        "execution_order": ["A"],
        "node_times": [f"A: {current_time}"],
        "store_info": store_info
    }
#def node_a(state: State):
#    current_time = format_time()
#    time.sleep(1)
#    return {
#        "execution_order": ["A"],
#        "node_times": [f"A: {current_time}"]
#    }

def node_b(state: State):
    current_time = format_time()
    time.sleep(1)
    return {
        "execution_order": ["B"],
        "node_times": [f"B: {current_time}"]
    }

def node_c(state: State):
    current_time = format_time()
    time.sleep(1)
    return {
        "execution_order": ["C"],
        "node_times": [f"C: {current_time}"]
    }

def node_d(state: State):
    current_time = format_time()
    time.sleep(1)
    info=interrupt("anything")
    return {
        "execution_order": ["D"],
        "node_times": [f"D: {current_time}"]
    }
# 构建图
graph_builder = StateGraph(State)
graph_builder.add_node("A", node_a)
graph_builder.add_node("B", node_b)
graph_builder.add_node("C", node_c)
graph_builder.add_node("D", node_d)

graph_builder.add_edge(START, "A")
graph_builder.add_edge("A", "B")
graph_builder.add_edge("A", "C")
graph_builder.add_edge("B", "D")
graph_builder.add_edge("C", "D")
graph_builder.add_edge("D", END)

checkpointer=InMemorySaver()
store=InMemoryStore()
graph = graph_builder.compile(checkpointer=checkpointer,store=store)

# 执行
initial_state = {"execution_order": [], "node_times": []}

config = {"configurable": {"thread_id": "1"}}
result = graph.invoke({},config)
result = graph.invoke({},config)
print(f"Final execution order: {result['execution_order']}")
print("\nDetailed execution timeline:")
for time_entry in result["node_times"]:
    print(f"  {time_entry}")

config1 = {"configurable": {"thread_id": "2"}}
result1 = graph.invoke({},config=config1)
print(f"Final execution order: {result1['execution_order']}")
print("\nDetailed execution timeline:")
for time_entry in result1["node_times"]:
    print(f"  {time_entry}")


snapshot_history_list=list(graph.get_state_history(config))
snapshot_history_list1=list(graph.get_state_history(config1))

for snapshot in snapshot_history_list:
    print(snapshot.values,snapshot.interrupts)

print(" ")

for snapshot in snapshot_history_list1:
    print(snapshot.values,snapshot.interrupts)