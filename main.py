from dotenv import load_dotenv
import json
import os
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from tools import all_tools
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class ResearchResponse(BaseModel):
    title: str = Field(description="A clear descriptive title for the research topic")
    summary: str = Field(description="A detailed summary of research findings (minimum 3-4 sentences)")
    sources: list[str] = Field(description="List of relevant sources or references used")
    tools_used: list[str] = Field(description="List of research tools used during the process")
    key_findings: list[str] = Field(description="List of key findings or insights from the research")
    confidence_score: float = Field(description="Confidence score (0-1) based on source quality and quantity")
    research_depth: str = Field(description="Assessment of research depth: 'surface', 'moderate', or 'comprehensive'")

class EnhancedResearchAgent:
    def __init__(self, model_name="llama3.1", base_url="http://localhost:11434/v1", api_key="ollama"):
        """Initialize the enhanced research agent"""
        self.llm = ChatOpenAI(
            model=model_name,
            base_url=base_url,
            api_key=api_key,
            temperature=0.1,
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()]
        )
        
        self.parser = PydanticOutputParser(pydantic_object=ResearchResponse)
        
        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
                You are an advanced AI research assistant with access to multiple specialized tools.
                Your goal is to conduct thorough, accurate research and provide comprehensive insights.
                
                RESEARCH STRATEGY:
                1. Start with web search and Wikipedia for general context
                2. Use ArXiv and Google Scholar for academic sources when relevant
                3. Scrape specific articles for detailed information when needed
                4. Extract content from documents (PDF, DOCX) if provided
                5. Get YouTube transcripts for video content when applicable
                6. Analyze collected data for patterns and insights
                7. Save findings in appropriate formats
                
                QUALITY GUIDELINES:
                - Use multiple sources to verify information
                - Prioritize recent and authoritative sources
                - Provide balanced perspectives when topics are controversial
                - Clearly indicate when information is uncertain or limited
                - Always cite your sources properly
                
                OUTPUT REQUIREMENTS:
                Respond with ONLY valid JSON in this exact format:
                {{
                    "title": "Clear, descriptive title for the research topic",
                    "summary": "Comprehensive summary with key findings (minimum 200 words)",
                    "sources": ["List of all sources used with URLs where applicable"],
                    "tools_used": ["List of tools used: web_search, search_arxiv, etc."],
                    "key_findings": ["List of 3-5 key insights or findings"],
                    "confidence_score": 0.85,
                    "research_depth": "comprehensive"
                }}
                
                IMPORTANT: 
                - Use tools strategically based on the query type
                - Academic queries should prioritize ArXiv and Scholar
                - Current events should focus on web search and news sources  
                - Always aim for comprehensive research using multiple tools
                - Include confidence assessment based on source quality
                """,
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{query}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            prompt=self.prompt,
            tools=all_tools
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent, 
            tools=all_tools, 
            verbose=True,
            max_iterations=10,
            early_stopping_method="generate"
        )
    
    def research(self, query: str, save_results: bool = True) -> dict:
        """Conduct research on the given query"""
        try:
            logger.info(f"Starting research on: {query}")
            
            # Execute the research
            response = self.agent_executor.invoke({"query": query})
            
            # Parse the response
            try:
                parsed_output = json.loads(response["output"])
                
                # Validate required fields
                required_fields = ["title", "summary", "sources", "tools_used"]
                for field in required_fields:
                    if field not in parsed_output:
                        parsed_output[field] = f"Field {field} not provided"
                
                # Add metadata
                parsed_output["query"] = query
                parsed_output["timestamp"] = json.dumps({"timestamp": "now"}, default=str)
                
                # Save results if requested
                if save_results:
                    self._save_research_results(parsed_output)
                
                return parsed_output
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                return {
                    "title": "Research Error",
                    "summary": f"Error parsing research results: {str(e)}",
                    "sources": [],
                    "tools_used": [],
                    "key_findings": ["Research completed but formatting error occurred"],
                    "confidence_score": 0.0,
                    "research_depth": "incomplete",
                    "raw_output": response["output"]
                }
                
        except Exception as e:
            logger.error(f"Research error: {e}")
            return {
                "title": "Research Failed",
                "summary": f"An error occurred during research: {str(e)}",
                "sources": [],
                "tools_used": [],
                "key_findings": ["Research could not be completed due to technical error"],
                "confidence_score": 0.0,
                "research_depth": "failed",
                "error": str(e)
            }
    
    def _save_research_results(self, results: dict):
        """Save research results to file"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"research_results_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Research results saved to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")

def main():
    """Main function for command-line interface"""
    print("🔬 Enhanced AI Research Assistant")
    print("=" * 50)
    
    # Initialize the research agent
    try:
        agent = EnhancedResearchAgent()
        print("✅ Research agent initialized successfully!")
        
    except Exception as e:
        print(f"❌ Failed to initialize research agent: {e}")
        return
    
    # Interactive research loop
    while True:
        try:
            print("\n" + "─" * 50)
            query = input("🔍 What would you like to research? (or 'quit' to exit): ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye! Happy researching!")
                break
            
            if not query:
                print("⚠️  Please enter a research query.")
                continue
            
            print(f"\n🚀 Starting research on: '{query}'")
            print("⏳ This may take a few moments...\n")
            
            # Conduct research
            results = agent.research(query)
            
            # Display results
            print("\n" + "=" * 50)
            print("📊 RESEARCH RESULTS")
            print("=" * 50)
            
            print(f"📌 Title: {results.get('title', 'N/A')}")
            print(f"🎯 Confidence: {results.get('confidence_score', 'N/A')}")
            print(f"📈 Depth: {results.get('research_depth', 'N/A')}")
            print(f"🛠️  Tools Used: {', '.join(results.get('tools_used', []))}")
            
            print(f"\n📝 Summary:")
            print(results.get('summary', 'No summary available'))
            
            if results.get('key_findings'):
                print(f"\n🔑 Key Findings:")
                for i, finding in enumerate(results['key_findings'], 1):
                    print(f"   {i}. {finding}")
            
            if results.get('sources'):
                print(f"\n📚 Sources ({len(results['sources'])}):")
                for i, source in enumerate(results['sources'], 1):
                    print(f"   {i}. {source}")
            
            print(f"\n💾 Results saved automatically.")
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Research interrupted by user.")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            continue

if __name__ == "__main__":
    main()
