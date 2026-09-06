from langchain_core.messages import SystemMessage, HumanMessage
from app.state import BlogState
from app.schemas import BlogPlan, BlogSection
from app.llm import llm

planner_llm = llm.with_structured_output(
    BlogPlan
)


def blog_planner(state: BlogState):

    analysis = state["analysis"]

    system_prompt = """
        You are the Blog Planner for a professional AI Writer Agent.

        Create a detailed blueprint for a blog post.

        Your plan should:

        - Create an engaging and accurate title.
        - Define a useful introduction.
        - Break the topic into logical sections.
        - Make each section useful to the target audience.
        - Identify sections that require code.
        - Identify sections that benefit from images or diagrams.
        - Create a useful conclusion.

        Do NOT write the complete blog post.

        Create a blueprint that downstream content, code, and image
        agents can use.
        """

    user_prompt = f"""
        Create a blog plan using the following analysis:

        Topic:
        {analysis.topic}

        Audience:
        {analysis.audience}

        Tone:
        {analysis.tone}

        Needs code:
        {analysis.needs_code}

        Needs images:
        {analysis.needs_images}

        Target word count:
        {analysis.word_count}
        """

    result = planner_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ])

    return {
        "plan": result
    }