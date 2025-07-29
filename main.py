from dotenv import load_dotenv
import json
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_tool

load_dotenv()

class ResearchResponse(BaseModel):
    title: str
    summary: str
    sources: list[str]
    tools_used: list[str]


llm = ChatOpenAI(
        model="llama3.1",
        base_url="http://localhost:11434/v1",
        api_key="ollama")

parser = PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a research assistant that will help generate a research paper.
            Answer the user query and Use the available tools to gather information **before responding**.
            Then, respond in **ONLY this exact JSON format**:.
            
            IMPORTANT: Respond with ONLY valid JSON in this exact format:
            {{
                "title": "A clear descriptive title for the research topic",
                "summary": "A detailed summary of your research findings (3-4 sentences minimum)",
                "sources": ["List of relevant sources or references"],
                "tools_used": ["List of research tools used, such as 'tavily_search'"]
            }}
            
            IMPORTANT: Use the tool results to inform your answer.Do not include any other text, explanations, or formatting. Just the JSON object.
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
        
    ]
)

tools = [search_tool, wiki_tool, save_tool]
agent = create_tool_calling_agent(
        llm=llm, 
        prompt=prompt, 
        tools=tools
    )

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
query = input("What can I help you research today? ")
response = agent_executor.invoke({"query": query})

try:
    parsed_output = json.loads(response["output"])
    print(parsed_output)
except Exception as e:
    print("Failed to parse response:", e)
    print("Raw output:", response)



