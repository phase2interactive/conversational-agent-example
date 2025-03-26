
from langchain_openai import ChatOpenAI
from graphs.inventory_agent.inventory_agent import create_inventory_agent
from graphs.supervisor import create_supervisor_agent
from typing import Dict, Any
from langchain.schema import HumanMessage
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver

model = ChatOpenAI(model="gpt-4o")
in_memory_store = InMemoryStore()
checkpointer = MemorySaver()

def create_agent_system():
    inventory_agent = create_inventory_agent(model)

    workflow = create_supervisor_agent(
        agents=[inventory_agent],
        model=model
    )

    return workflow.compile(store=in_memory_store, checkpointer=checkpointer)

graph = create_agent_system()

async def process_message(message: str, thread_id: str = None) -> Dict[str, Any]:
    """Process an incoming message through the agent system"""

    config_dict = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    human_message = HumanMessage(content=message)
    return await graph.ainvoke({"messages": [human_message]}, config=config_dict)

    # for msg in result.get("messages", []):
    #     if not msg:
    #         continue

    #     # If msg is a dict, we need to convert it to a BaseMessage first
    #     if isinstance(msg, dict):
    #         # Skip if no content
    #         if not msg.get("content"):
    #             continue

    #         # Add a prefix to the name for better visibility
    #         prefix = "SUPERVISOR" if msg.get("name") == "supervisor" else "EXPERT"
    #         if msg.get("name"):
    #             msg["name"] = f"{prefix} | {msg.get('name')}"

    #         # Only process AI messages
    #         if msg.get("type") == "ai":
    #             msg.pretty_print()
    #     else:
    #         # For BaseMessage objects
    #         if hasattr(msg, 'content') and msg.content:
    #             # Only process AI messages
    #             if msg.__class__.__name__ == "AIMessage":
    #                 prefix = "SUPERVISOR" if getattr(msg, "name", "") == "supervisor" else "EXPERT"
    #                 if hasattr(msg, "name"):
    #                     msg.name = f"{prefix} | {msg.name}"
    #                 msg.pretty_print()

    # return result
