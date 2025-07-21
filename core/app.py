import os
from typing import TypedDict, Annotated

from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI

from core.retriever import guest_info_tool
from core.tools import web_search_tool, hub_stats_tool

# ============================================================================
# CONSTANTS
# ============================================================================
ROLLING_MEMORY_WINDOW = 50

# ============================================================================
# TYPE DEFINITIONS
# ============================================================================
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

# ============================================================================
# CONFIGURATION
# ============================================================================
# Tool configuration
tools = [guest_info_tool, web_search_tool, hub_stats_tool]

# LLM configuration
llm = ChatOpenAI(model="gpt-4", openai_api_key=os.environ["OPENAI_API_KEY"])

# ============================================================================
# CORE FUNCTIONS
# ============================================================================
def assistant(state: AgentState):
    """Main assistant node that processes messages and decides whether to use tools."""
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(state["messages"])
    
    # Debug: Show what the response object looks like
    print(f"🔍 DEBUG: Assistant processing request...")
    print(f"🔍 DEBUG: Response type: {type(response)}")
    print(f"🔍 DEBUG: Initial response content: {response.content[:50]}...")
    print(f"🔍 DEBUG: Has tool calls: {hasattr(response, 'tool_calls') and response.tool_calls}")
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print(f"🔍 DEBUG: Tool calls detected: {[tc.get('name') for tc in response.tool_calls]}")
    
    return {
        "messages": [response]
    }

# ============================================================================
# GLOBAL AGENT INSTANCE
# ============================================================================
# Create a global agent instance that can be shared across interfaces
_agent_instance = None

def get_agent():
    """Get or create the global agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = build_agent_graph()
    return _agent_instance

def run_agent_with_tools(messages, agent=None):
    """
    Runs the agent that automatically handles tool calls, until a final answer is produced.
    
    Args:
        messages: List of conversation messages (must include the latest user message)
        agent: Optional agent instance. If None, uses global agent.
    
    Returns:
        The final response from the agent (list of messages)
    """
    if agent is None:
        agent = get_agent()
    
    if not messages:
        raise ValueError("Messages list cannot be empty")
    
    # Process with agent
    response = agent.invoke({"messages": messages[-ROLLING_MEMORY_WINDOW:]})
    return response["messages"]

# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================
def build_agent_graph():
    """Builds and returns the LangGraph agent."""
    builder = StateGraph(AgentState)

    # Define nodes: these do the work
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))

    # Define edges: these determine how the control flow moves
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        # If the latest message requires a tool, route to tools
        # Otherwise, provide a direct response
        tools_condition,
    )
    builder.add_edge("tools", "assistant")
    
    return builder.compile()

def save_graph_visualization(graph, filename="docs/alfred_agent_graph.png"):
    """
    Saves a visualization of the LangGraph to a PNG file using Mermaid.
    
    Args:
        graph: The compiled LangGraph agent
        filename: Output filename for the visualization
    """
    import os
    
    # Ensure docs directory exists
    os.makedirs("docs", exist_ok=True)
    
    try:
        # Create the visualization using Mermaid (built into LangGraph)
        mermaid_png = graph.get_graph().draw_mermaid_png()
        
        # Save to file
        with open(filename, 'wb') as f:
            f.write(mermaid_png)
        print(f"🎨 Graph visualization saved to: {filename}")
        
    except Exception as e:
        print(f"⚠️  Could not save graph visualization: {str(e)}")
        print("💡 This should work without any external dependencies")

# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    # Build the agent
    alfred = get_agent()

    # Save graph visualization
    save_graph_visualization(alfred)
    
    # Test the agent
    messages = [HumanMessage(content="I need to speak with 'Dr. Nikola Tesla' about recent advancements in wireless energy. Can you help me prepare for this conversation?")]
    response = run_agent_with_tools(messages)
    print("🎩 Alfred's Response:")
    print(response[-1].content)