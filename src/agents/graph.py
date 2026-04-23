"""Graph builder module. Assembles the complete multi-agent LangGraph workflow."""

import logging
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

from src.state import State
from src.tools.equipment_catalog import equipment_tools
from src.tools.order_support import order_support_tools
from src.agents.prompts import ORDER_SUBAGENT_PROMPT, SUPERVISOR_PROMPT
from src.agents.nodes import (
    equipment_state_modifier,
    should_interrupt,
    create_verify_info_node,
    human_input,
    load_memory,
    create_memory_node,
)

logger = logging.getLogger(__name__)


def build_graph(
    model_name: str = "llama-3.1-8b-instant",
    temperature: float = 0,
    groq_api_key: str = None,
):
    llm_kwargs = {
        "model": model_name,
        "temperature": temperature,
    }
    if groq_api_key:
        llm_kwargs["api_key"] = groq_api_key

    llm = ChatGroq(**llm_kwargs)
    logger.info(f"LLM initialized: {model_name}, temperature={temperature}")

    # NOTE: Both stores are in-memory only — all data is lost on restart.
    # For production, replace with SqliteSaver / persistent store.
    in_memory_store = InMemoryStore()
    checkpointer = MemorySaver()

    # Equipment Catalog Sub-Agent (pre-built ReAct)
    equipment_catalog_subagent = create_react_agent(
        llm,
        tools=equipment_tools,
        name="equipment_catalog_subagent",
        prompt=equipment_state_modifier,
        state_schema=State,
        checkpointer=checkpointer,
        store=in_memory_store,
    )
    logger.info("Equipment catalog sub-agent compiled.")

    # Order Information Sub-Agent (pre-built ReAct)
    order_information_subagent = create_react_agent(
        llm,
        tools=order_support_tools,
        name="order_information_subagent",
        prompt=ORDER_SUBAGENT_PROMPT,
        state_schema=State,
        checkpointer=checkpointer,
        store=in_memory_store,
    )
    logger.info("Order information sub-agent compiled.")

    # Supervisor
    from langgraph_supervisor import create_supervisor

    supervisor_workflow = create_supervisor(
        agents=[order_information_subagent, equipment_catalog_subagent],
        output_mode="last_message",
        model=llm,
        prompt=SUPERVISOR_PROMPT,
        state_schema=State,
    )
    supervisor_prebuilt = supervisor_workflow.compile(
        name="supervisor",
        checkpointer=checkpointer,
        store=in_memory_store,
    )
    logger.info("Supervisor compiled.")

    # Final Multi-Agent Graph
    verify_info_fn = create_verify_info_node(llm)
    create_memory_fn = create_memory_node(llm)

    multi_agent = StateGraph(State)
    multi_agent.add_node("verify_info", verify_info_fn)
    multi_agent.add_node("human_input", human_input)
    multi_agent.add_node("load_memory", load_memory)
    multi_agent.add_node("supervisor", supervisor_prebuilt)
    multi_agent.add_node("create_memory", create_memory_fn)

    multi_agent.add_edge(START, "verify_info")
    multi_agent.add_conditional_edges(
        "verify_info",
        should_interrupt,
        {"continue": "load_memory", "interrupt": "human_input"},
    )
    multi_agent.add_edge("human_input", "verify_info")
    multi_agent.add_edge("load_memory", "supervisor")
    multi_agent.add_edge("supervisor", "create_memory")
    multi_agent.add_edge("create_memory", END)

    compiled_graph = multi_agent.compile(
        name="multi_agent_final",
        checkpointer=checkpointer,
        store=in_memory_store,
    )
    logger.info("Final multi-agent graph compiled successfully.")

    return compiled_graph, checkpointer, in_memory_store
