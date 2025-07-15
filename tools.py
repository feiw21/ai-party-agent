from langchain.tools import Tool
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from duckduckgo_search import DDGS
from huggingface_hub import list_models

# --- Web search tool definition ---
def web_search(query: str) -> str:
    """Searches the web for the latest information about a person or topic."""
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)
        output = []
        for r in results:
            output.append(f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}")
        if output:
            return "\n\n".join(output)
        else:
            return "No relevant web results found."

web_search_tool = Tool(
    name="web_search",
    func=web_search,
    description="Searches the web for the latest information about a person or topic. Use this if the guest is unfamiliar or not found in the local database."
)


# --- Huggingface stats search tool definition ---
def get_hub_stats(author: str) -> str:
    """Fetches the most downloaded model from a specific author on the Hugging Face Hub."""
    try:
        # List models from the specified author, sorted by downloads
        models = list(list_models(author=author, sort="downloads", direction=-1, limit=1))

        if models:
            model = models[0]
            return f"The most downloaded model by {author} is {model.id} with {model.downloads:,} downloads."
        else:
            return f"No models found for author {author}."
    except Exception as e:
        return f"Error fetching models for {author}: {str(e)}"

hub_stats_tool = Tool(
    name="get_hub_stats",
    func=get_hub_stats,
    description="Fetches the most downloaded model from a specific author on the Hugging Face Hub."
)
