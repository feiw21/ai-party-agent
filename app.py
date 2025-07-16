import os
from typing import TypedDict, Annotated

from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI

from retriever import guest_info_tool
from tools import web_search_tool, hub_stats_tool

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
    print(f"🔍 DEBUG: response type: {type(response)}")
    print(f"🔍 DEBUG: response content: {response.content}")
    print(f"🔍 DEBUG: response has tool_calls: {hasattr(response, 'tool_calls')}")
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print(f"🔍 DEBUG: response tool_calls: {response.tool_calls}")
    
    return {
        "messages": [response]
    }

def run_agent_with_tools(messages, max_steps=10):
    """
    Runs the agent in a loop, handling tool calls, until a final answer is produced.
    
    Args:
        messages: List of conversation messages
        max_steps: Maximum number of tool execution steps
    
    Returns:
        Updated messages list with final response
    """
    for _ in range(max_steps):
        response = alfred.invoke({"messages": messages[-ROLLING_MEMORY_WINDOW:]})
        # Add the new messages from the agent to the conversation
        new_msgs = response["messages"][len(messages):]
        messages.extend(new_msgs)
        last_msg = messages[-1]

        # Debug: Let's see what last_msg actually looks like
        print(f"🔍 DEBUG: last_msg type: {type(last_msg)}")
        print(f"🔍 DEBUG: last_msg content: {last_msg.content}")
        print(f"🔍 DEBUG: last_msg has tool_calls: {hasattr(last_msg, 'tool_calls')}")
        if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
            print(f"🔍 DEBUG: last_msg tool_calls: {last_msg.tool_calls}")
        print(f"🔍 DEBUG: last_msg has tool_call: {hasattr(last_msg, 'tool_call')}")
        if hasattr(last_msg, 'tool_call') and last_msg.tool_call:
            print(f"🔍 DEBUG: last_msg tool_call: {last_msg.tool_call}")

        # Check if the last message is a tool call
        if hasattr(last_msg, "tool_call") or (
            isinstance(last_msg.content, dict) and "name" in last_msg.content
        ):
            # Handle tool call
            if hasattr(last_msg, "tool_call"):
                tool_call = last_msg.tool_call
            else:
                tool_call = last_msg.content
            
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("arguments", tool_call.get("input", ""))
            
            # Find the tool by name
            tool = next((t for t in tools if t.name == tool_name), None)
            if tool:
                # Execute the tool
                try:
                    tool_result = tool.func(tool_args)
                    messages.append(AIMessage(content=tool_result))
                except Exception as e:
                    messages.append(AIMessage(content=f"Error executing tool {tool_name}: {str(e)}"))
            else:
                messages.append(AIMessage(content=f"Tool '{tool_name}' not found."))
        else:
            # Final answer produced
            break
    return messages

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
    alfred = build_agent_graph()
    
    # Save graph visualization
    save_graph_visualization(alfred)
    
    # Test the agent
    messages = [HumanMessage(content="I need to speak with 'Dr. Nikola Tesla' about recent advancements in wireless energy. Can you help me prepare for this conversation?")]
    response = run_agent_with_tools(messages)
    print("🎩 Alfred's Response:")
    print(response[-1].content)