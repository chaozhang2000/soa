from typing import Annotated, List, TypedDict
from langgraph.graph import StateGraph, START, END
import operator
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
import uuid

class State(TypedDict):
    execution_order: Annotated[List[str], operator.add]

def node_a(state: State, store: InMemoryStore):
    namespace = ("node_a","memorys")
    key = f"{uuid.uuid4()}"  # 避免冲突
    # 2. 准备要存储的原始数据（字典格式）
    data_to_store = {"node_name": "A"}
    # 3. 向store写入数据（put需要3个参数：namespace, key, 原始数据）
    store.put(namespace, key, data_to_store)
    # 4. 从store读取数据（get返回Item对象，需通过.value获取原始数据）
    retrieved_item = store.search(namespace)  # 返回Item对象
    print(retrieved_item )
    # 返回节点A对状态的更新
    return {"execution_order": ["A"]}
# 节点B
def node_b(state: State):return {"execution_order": ["B"]}
# 节点C（无修改，保持原逻辑）
def node_c(state: State):return {"execution_order": ["C"]}

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
}

# 线程1执行
print("="*50)
print("线程1执行第一次")
print("="*50)
config_thread = {"configurable": {"thread_id": "1"}}  # 线程1的配置（含唯一ID）
# 首次invoke会执行到D节点的interrupt，第二次invoke继续执行（因checkpointer保存状态）
result_thread1_1 = graph.invoke(initial_state, config_thread)
print("="*50)
print("线程1执行第二次")
print("="*50)
result_thread1_2 = graph.invoke({}, config_thread)  # 空输入表示继续上一状态
# 打印线程1结果
print(f"\n线程1最终执行顺序: {result_thread1_2['execution_order']}")

# 线程2执行（独立于线程1，状态和存储数据隔离）
print("\n" + "="*50)
print("线程2执行第一次")
print("="*50)
config_thread2 = {"configurable": {"thread_id": "2"}}  # 线程2的配置（含唯一ID）
result_thread2_2 = graph.invoke({}, config_thread2)
# 打印线程2结果
print(f"\n线程2最终执行顺序: {result_thread2_2['execution_order']}")

# 6. 查看状态历史
print("\n" + "="*50)
print("线程1状态历史")
print("="*50)
for idx, snapshot in enumerate(graph.get_state_history(config_thread)):
    print(f"历史快照{idx+1}:")
    print(f"  状态值: {snapshot.values}")

print("\n" + "="*50)
print("线程2状态历史")
print("="*50)
for idx, snapshot in enumerate(graph.get_state_history(config_thread2)):
    print(f"历史快照{idx+1}:")
    print(f"  状态值: {snapshot.values}")
    print(f"  config: {snapshot.config}")