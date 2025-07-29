from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_tavily import TavilySearch
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

def save_to_txt(data: str, filename: str = f"research_output.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"-- Research Output --\nTimestamp: {timestamp}\n\n{data}\n"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)
    
    return f"Data saved to {filename} at {timestamp}"

save_tool = Tool(
    name = "save_txt_to_file",
    func=save_to_txt,
    description="Save structured research data to a text file"
)

search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="search",
    func=search.run,
    description="Search the web for information"
)


# search_tool = TavilySearch(
#     api_key=os.getenv("TAVILY_API_KEY"),
#     max_results=2,
#     topic="general",
#     include_answer=True,
#     include_raw_content=False,
#     include_images=False,
#     search_depth="basic"
# )

api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=100)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

