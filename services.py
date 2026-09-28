from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b"
)

search = TavilySearch(max_results=3)