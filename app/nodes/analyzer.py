from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.state import BlogState
from app.schemas import PromptAnalysis
from app.llm import llm

analyzer_llm = llm.with_structured_output(
    PromptAnalysis
)

def prompt_analyzer(state: BlogState):
    user_prompt = state["user_prompt"]

    system_prompt = """
        You are the Prompt Analyzer for a professional AI Writer Agent.

        Analyze the user's request for a blog post.

        Determine:

        1. The main topic
        2. The target audience
        3. The desired tone
        4. Whether code examples are required
        5. Whether images or diagrams are useful
        6. The approximate desired word count

        Do not write the blog post.

        Only analyze the request and return the structured analysis.
        """
    result = analyzer_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    return {
        "analysis": result # returns a PromptAnalysis object,
    }