import os
from typing import TypedDict, Annotated

from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI

from retriever import guest_info_tool
from tools import web_search_tool, hub_stats_tool

ROLLING_MEMORY_WINDOW = 50

tools = [guest_info_tool, web_search_tool, hub_stats_tool]

# Use LangChain's ChatOpenAI for full tool support
llm = ChatOpenAI(model="gpt-4", openai_api_key=os.environ["OPENAI_API_KEY"])

# Generate the AgentState and Agent graph
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

def assistant(state: AgentState):
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(state["messages"])
    return {
        "messages": [response]
    }

## The graph
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
alfred = builder.compile()

def run_agent_with_tools(messages, max_steps=10):
    """
    Runs the agent in a loop, handling tool calls, until a final answer is produced.
    """
    for _ in range(max_steps):
        response = alfred.invoke({"messages": messages[-ROLLING_MEMORY_WINDOW:]})
        # Add the new messages from the agent to the conversation
        new_msgs = response["messages"][len(messages):]
        messages.extend(new_msgs)
        last_msg = messages[-1]

        # Debug: Let's see what last_msg actually looks like
        # print(f"🔍 DEBUG: last_msg type: {type(last_msg)}")
        print(f"🔍 DEBUG: last_msg content: {last_msg.content}")

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

# Test the agent
messages = [HumanMessage(content="I need to speak with 'Dr. Nikola Tesla' about recent advancements in wireless energy. Can you help me prepare for this conversation?")]
response = run_agent_with_tools(messages)
print("🎩 Alfred's Response:")
print(response[-1].content)