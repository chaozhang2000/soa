from typing import Annotated, List, TypedDict
from langgraph.graph import StateGraph, START, END
import time
import operator
from datetime import datetime
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

class State(TypedDict):
    execution_order: Annotated[List[str], operator.add]
    node_times: Annotated[List[str], operator.add]  # 记录每个节点的执行时间

# 格式化时间（精确到毫秒）
def format_time():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

# 节点A：新增store操作（存储+读取）
def node_a(state: State, store: InMemoryStore):
    current_time = format_time()
    
    # 1. 定义存储的命名空间和键（命名空间用于分类数据，键确保唯一性）
    namespace = ("node_a","memorys")  # 按功能定义命名空间，便于数据管理
    thread_id = state.get("configurable", {}).get("thread_id", "unknown")  # 从状态中获取线程ID
    key = f"thread_{thread_id}_time_{current_time}"  # 键包含线程ID和时间，避免冲突
    
    # 2. 准备要存储的原始数据（字典格式）
    data_to_store = {
        "node_name": "A",
        "execution_time": current_time,
        "thread_id": thread_id,
        "message": "节点A执行时存储的业务数据"
    }
    
    # 3. 向store写入数据（put需要3个参数：namespace, key, 原始数据）
    print(key)
    store.put(namespace, key, data_to_store)
    
    # 4. 从store读取数据（get返回Item对象，需通过.value获取原始数据）
    retrieved_item = store.search(namespace)  # 返回Item对象
    print(retrieved_item )
    # 模拟节点业务处理耗时
    time.sleep(1)
    
    # 返回节点A对状态的更新
    return {
        "execution_order": ["A"],
        "node_times": [f"A: {current_time}"],
    }

# 节点B（无修改，保持原逻辑）
def node_b(state: State):
    current_time = format_time()
    time.sleep(1)
    return {
        "execution_order": ["B"],
        "node_times": [f"B: {current_time}"]
    }

# 节点C（无修改，保持原逻辑）
def node_c(state: State):
    current_time = format_time()
    time.sleep(1)
    return {
        "execution_order": ["C"],
        "node_times": [f"C: {current_time}"]
    }

# 1. 构建状态图
graph_builder = StateGraph(State)
# 节点A通过lambda传递store实例（因add_node的节点函数仅接收state参数）
graph_builder.add_node("A", lambda state: node_a(state, store))
graph_builder.add_node("B", node_b)
graph_builder.add_node("C", node_c)

# 2. 定义节点间的边（流程：START→A，A→B/C，B/C→D，D→END）
graph_builder.add_edge(START, "A")
graph_builder.add_edge("A", "B")
graph_builder.add_edge("A", "C")
graph_builder.add_edge("B", END)
graph_builder.add_edge("C", END)

# 3. 初始化检查点（用于状态持久化）和存储（用于自定义数据存储）
checkpointer = InMemorySaver()
store = InMemoryStore()  # 实例化存储，供节点A使用

# 4. 编译图（仅需传入checkpointer，store已通过lambda传递给节点A）
graph = graph_builder.compile(checkpointer=checkpointer)

# 5. 执行图（两个独立线程，验证存储隔离性）
initial_state = {
    "execution_order": [],
    "node_times": [],
}

# 线程1执行
print("="*50)
print("线程1执行第一次")
print("="*50)
config_thread1 = {"configurable": {"thread_id": "1"}}  # 线程1的配置（含唯一ID）
# 首次invoke会执行到D节点的interrupt，第二次invoke继续执行（因checkpointer保存状态）
result_thread1_1 = graph.invoke(initial_state, config_thread1)
print("="*50)
print("线程1执行第二次")
print("="*50)
result_thread1_2 = graph.invoke({}, config_thread1)  # 空输入表示继续上一状态
# 打印线程1结果
print(f"\n线程1最终执行顺序: {result_thread1_2['execution_order']}")
print("\n线程1详细时间线:")
for time_entry in result_thread1_2["node_times"]:
    print(f"  {time_entry}")

# 线程2执行（独立于线程1，状态和存储数据隔离）
print("\n" + "="*50)
print("线程2执行第一次")
print("="*50)
config_thread2 = {"configurable": {"thread_id": "2"}}  # 线程2的配置（含唯一ID）
result_thread2_2 = graph.invoke(initial_state, config_thread2)
# 打印线程2结果
print(f"\n线程2最终执行顺序: {result_thread2_2['execution_order']}")
print("\n线程2详细时间线:")
for time_entry in result_thread2_2["node_times"]:
    print(f"  {time_entry}")

# 6. 查看状态历史（验证checkpointer的状态保存功能）
print("\n" + "="*50)
print("线程1状态历史")
print("="*50)
for idx, snapshot in enumerate(graph.get_state_history(config_thread1)):
    print(f"历史快照{idx+1}:")
    print(f"  状态值: {snapshot.values}")

print("\n" + "="*50)
print("线程2状态历史")
print("="*50)
for idx, snapshot in enumerate(graph.get_state_history(config_thread2)):
    print(f"历史快照{idx+1}:")
    print(f"  状态值: {snapshot.values}")
    print(f"  config: {snapshot.config}")