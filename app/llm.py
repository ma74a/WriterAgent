from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    max_retries=5,  # Automatically retry on 429 errors using exponential backoff
    timeout=60,
    temperature=0.2
)