# AI Travel Planning System using LangGraph

This project is a multi-agent AI travel planning system built with LangGraph, LangChain, Groq, and PostgreSQL.

## Features
- Flight agent
- Hotel agent
- Itinerary agent
- Final response agent
- PostgreSQL-backed checkpoint memory
- Streamlit frontend

## Setup
1. Install dependencies
2. Create a `.env` file
3. Use the following values:
   - GROQ_API_KEY=your_groq_api_key
   - TAVILY_API_KEY=your_tavily_api_key
   - AVIATIONSTACK_API_KEY=your_aviationstack_api_key
4. Run `python main.py`
5. Or use `streamlit run frontend.py`
