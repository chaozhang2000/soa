from langgraph.store.memory import InMemoryStore


def embed(texts: list[str]) -> list[list[float]]:
    # Replace with an actual embedding function or LangChain embeddings object
    return [[1.0, 2.0] * len(texts)]


# InMemoryStore saves data to an in-memory dictionary. Use a DB-backed store in production use.
store = InMemoryStore(index={"embed": embed, "dims": 2})
user_id = "my-user"
application_context = "chitchat"
user_id1 = "my-user1"
application_context1 = "chitchat1"
namespace = (user_id, application_context)
namespace1 = (user_id1, application_context1)
store.put(
    namespace,
    "a-memory",
    {
        "rules": [
            "User likes short, direct language",
            "User only speaks English & python",
        ],
        "my-key": "my-value",
    },
)
store.put(
    namespace1,
    "a-memory",
    {
        "rules1": [
            "User likes short, direct language1",
            "User only speaks English & python1",
        ],
        "my-key1": "my-value1",
    },
)
# get the "memory" by ID
item = store.get(namespace, "a-memory")
item1 = store.get(namespace1, "a-memory")
print(item)
print(item1)
# search for "memories" within this namespace, filtering on content equivalence, sorted by vector similarity
items = store.search(
    namespace, filter={"my-key": "my-value"}, query="language preferences"
)
print(items)