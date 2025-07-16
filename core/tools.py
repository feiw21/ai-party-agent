from duckduckgo_search import DDGS
from huggingface_hub import list_models
from langchain.tools import Tool

# --- Web search tool definition ---
def web_search(query: str) -> str:
    """Searches the web for the latest information about a person or topic."""
    print(f"🔍 DEBUG: web_search called with query: '{query}'")
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)
        output = []
        for r in results:
            output.append(f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}")
        if output:
            print(f"🔍 DEBUG: web_search found {len(output)} results")
            return "\n\n".join(output)
        else:
            print(f"🔍 DEBUG: web_search found no results")
            return "No relevant web results found."

web_search_tool = Tool(
    name="web_search",
    func=web_search,
    description="Searches the web for the latest information about a person or topic. Use this if the guest is unfamiliar or not found in the local database."
)


# --- Huggingface stats search tool definition ---
def get_hub_stats(author: str) -> str:
    """Fetches the most downloaded model from a specific author on the Hugging Face Hub."""
    print(f"🔍 DEBUG: get_hub_stats called with author: '{author}'")
    try:
        # List models from the specified author, sorted by downloads
        models = list(list_models(author=author, sort="downloads", direction=-1, limit=1))

        if models:
            model = models[0]
            print(f"🔍 DEBUG: get_hub_stats found model: {model.id}")
            return f"The most downloaded model by {author} is {model.id} with {model.downloads:,} downloads."
        else:
            print(f"🔍 DEBUG: get_hub_stats found no models")
            return f"No models found for author {author}."
    except Exception as e:
        print(f"🔍 DEBUG: get_hub_stats error: {str(e)}")
        return f"Error fetching models for {author}: {str(e)}"

hub_stats_tool = Tool(
    name="get_hub_stats",
    func=get_hub_stats,
    description="Fetches the most downloaded model from a specific author on the Hugging Face Hub."
)
