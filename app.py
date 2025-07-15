import os
from typing import TypedDict, Annotated

from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from openai import OpenAI

from retriever import guest_info_tool
from tools import web_search_tool, hub_stats_tool

ROLLING_MEMORY_WINDOW = 50

class OpenAILLM:
    def __init__(self, model="gpt-4", api_key=None):
        self.client = OpenAI(api_key=api_key or os.environ["OPENAI_API_KEY"])
        self.model = model

    def invoke(self, messages):
        # Format messages for OpenAI API
        chat_messages = []
        for msg in messages:
            if isinstance(msg, AIMessage):
                chat_messages.append({"role": "assistant", "content": msg.content})
            else:
                chat_messages.append({"role": "user", "content": msg.content})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=chat_messages,
            max_tokens=512,
        )
        return {"messages": [AIMessage(content=response.choices[0].message.content)]}

llm = OpenAILLM(model="gpt-4")

tools = [guest_info_tool, web_search_tool, hub_stats_tool]

# Generate the AgentState and Agent graph
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

def assistant(state: AgentState):
    response = llm.invoke(state["messages"])
    return {
        "messages": response["messages"]
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

        # Check if the last message is a tool call (adjust as needed for your framework)
        if hasattr(last_msg, "tool_call") or (
            isinstance(last_msg.content, dict) and "name" in last_msg.content
        ):
            # Simulate tool execution (replace with your actual tool execution logic)
            tool_name = last_msg.content["name"]
            tool_args = last_msg.content["arguments"]
            # Find the tool by name
            tool = next((t for t in tools if t.name == tool_name), None)
            if tool:
                # Some tools expect arguments as a single string, others as kwargs
                if isinstance(tool_args, dict) and "__arg1" in tool_args:
                    tool_input = tool_args["__arg1"]
                    tool_result = tool.func(tool_input)
                else:
                    tool_result = tool.func(**tool_args)
                messages.append(AIMessage(content=tool_result))
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