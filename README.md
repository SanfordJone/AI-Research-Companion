# AI-Powered Research Assistant

## Overview

This project is an AI-powered research assistant that leverages **Ollama's LLM models** to automate the research process. The assistant gathers, analyzes, and summarizes data from multiple sources, integrating web search tools, Wikipedia, and file-saving functionalities. It produces structured research output in JSON format and can export results to text files.

## Features

- **Ollama LLM Integration**: Uses Ollama’s LLM (e.g., llama3.2) for generating research summaries.
- **Multi-Source Research**: Integrates DuckDuckGo web search and Wikipedia API for comprehensive information gathering.
- **Structured Output**: Returns research results in a standardized JSON format.
- **Export Capability**: Saves research output to `.txt` files with timestamps for easy reference.

## How It Works

1. **User Query**: The user is prompted to enter a research topic.
2. **Automated Research**: The assistant uses integrated tools (web search, Wikipedia) to gather information.
3. **Structured Response**: The AI generates a JSON object containing the title, summary, sources, and tools used.
4. **Export Option**: Results can be saved to a text file for future reference.

## Main Components

### `main.py`

- Loads environment variables.
- Defines a `ResearchResponse` Pydantic model for structured output.
- Sets up the Ollama LLM via LangChain.
- Configures a prompt to ensure JSON-only responses.
- Integrates tools: web search, Wikipedia, and file saving.
- Executes the agent to process user queries and outputs results.

### `tools.py`

- **DuckDuckGo Search**: Gathers web information.
- **Wikipedia API**: Fetches concise Wikipedia summaries.
- **File Saving Tool**: Appends research results to a timestamped text file.

## Example Usage

```bash
python main.py
# What can I help you research today? <your topic>
```

The assistant will output a JSON object with the research findings and optionally save it to a text file.

## Requirements

- Python 3.8+
- [Ollama](https://ollama.com/) running locally
- Required Python packages: `langchain`, `langchain_openai`, `pydantic`, `python-dotenv`, etc.
- (Optional) Tavily API key for advanced search

## Setup

1. Clone the repository.
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Ensure Ollama is running locally.
4. Create a `.env` file for any required API keys.
5. Run the assistant:
    ```bash
    python main.py
    ```

## Customization

- Add or modify tools in `tools.py` to extend research capabilities.
- Adjust the prompt in `main.py` for different output formats or instructions.

---

