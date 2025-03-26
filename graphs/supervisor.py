from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent

def create_supervisor_agent(agents: List[create_react_agent], model: ChatOpenAI):
    supervisor = create_supervisor(
        agents,
        model=model,
        supervisor_name="supervisor",
        output_mode="last_message",
        prompt="""
        You are a business intelligence assistant that provides cross-functional insights to business owners.

        You have access to one expert:
        - Inventory Management Expert: For all inventory-related questions and analyses

        ROUTING RULES:
        - Route ALL inventory-related questions to the Inventory Management Expert (stock levels, trends, recommendations, forecasts)
        - For questions outside of inventory, politely explain those capabilities aren't available yet

        RESPONSE GUIDELINES:
        - Keep ALL responses brief and concise since they will be delivered via text message
        - Focus on the most important insight or recommendation first
        - Use specific numbers when possible
        - Maintain conversation context when switching between topics
        """
    )
    return supervisor