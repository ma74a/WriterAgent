from langchain_core.messages import SystemMessage, HumanMessage
from app.llm import llm
from app.schemas import GeneratedSection, BlogSection
from app.state import BlogState

writer_llm = llm.with_structured_output(
    GeneratedSection
)


def generate_section(
    section: BlogSection,
    topic: str,
    audience: str,
    tone: str,
):
    
    system_prompt = """
        You are an expert technical blog writer.

        Write one section of a professional blog post.

        Requirements:

        - Stay focused on the section topic.
        - Explain concepts clearly.
        - Match the target audience.
        - Follow the requested tone.
        - Do not write other sections.
        - Do not include a conclusion unless this is the conclusion section.
        - Do not invent facts.
        - Use Markdown where appropriate.
        """

    user_prompt = f"""
        Blog topic:
        {topic}

        Target audience:
        {audience}

        Tone:
        {tone}

        Section title:
        {section.title}

        Section description:
        {section.description}

        Write this section now.
        """

    result = writer_llm.invoke([
        HumanMessage(content=user_prompt),
        SystemMessage(content=system_prompt)
    ])

    return result


def content_generator(state: BlogState):
    analysis = state["analysis"]
    plan = state["plan"]

    generated_content = {}
    for section in plan.sections:
        print(f"\nGenerating section: {section.title}")
        result = generate_section(
            section=section,
            topic=analysis.topic,
            audience=analysis.audience,
            tone=analysis.tone
        )
        generated_content[section.title] = result.content

    return {
        "content": generated_content
    }