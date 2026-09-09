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
    research_context: str,
): 
    system_prompt = """
        You are an expert technical blog writer.

        Write one section of a professional blog post.

        You have access to web research collected from Tavily.

        Use the research as factual reference material.

        Requirements:

        - Stay focused on the section topic.
        - Explain concepts clearly.
        - Match the target audience.
        - Follow the requested tone.
        - Use the provided research when relevant.
        - Prefer claims supported by the research.
        - Do not invent facts.
        - Do not make unsupported specific claims.
        - Do not write other sections.
        - Do not include a conclusion unless this is the conclusion section.
        - Use Markdown where appropriate.

        Return only the structured section.
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


        Relevant web research:

        {research_context}


        Write this section now.

        Use the research to improve the factual accuracy and usefulness
        of the section.
        """

    result = writer_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    return result

def format_research(research, max_sources=6, max_chars=6000):
    if not research:
        return "No web research available."

    sources = sorted(
        [s for r in research.results for s in r.sources],
        key=lambda s: s.score,
        reverse=True
    )[:max_sources]

    research_text = ""
    total_chars = 0

    for source in sources:
        remaining = max_chars - total_chars
        if remaining <= 0:
            break
        content = source.content[:remaining]
        total_chars += len(content)
        research_text += f"SOURCE: {source.title}\nURL: {source.url}\n\n{content}\n\n---\n"

    return research_text


def content_generator(state: BlogState):
    analysis = state["analysis"]
    plan = state["plan"] # BlogPlan
    research = state.get("research")

    research_context = format_research(research)

    generated_content = {}

    # Introduction
    introduction_section = BlogSection(
        title="Introduction",
        description=plan.introduction,
        needs_code=False,
        needs_image=False
    )
    introduction = generate_section(
        section=introduction_section,
        topic=analysis.topic,
        audience=analysis.audience,
        tone=analysis.tone,
        research_context=research_context
    )
    generated_content["Introduction"] = introduction.content

    # Main section content
    for section in plan.sections:
        print(f"\nGenerating section: {section.title}")
        result = generate_section(
            section=section,
            topic=analysis.topic,
            audience=analysis.audience,
            tone=analysis.tone,
            research_context=research_context
        )
        generated_content[section.title] = result.content

    # conclusion
    conclusion_section = BlogSection(
        title="Conclusion",
        description=plan.conclusion,
        needs_code=False,
        needs_image=False
    )
    conclusion = generate_section(
        section=conclusion_section,
        topic=analysis.topic,
        audience=analysis.audience,
        tone=analysis.tone,
        research_context=research_context
    )
    generated_content["Conclusion"] = conclusion.content

    return {
        "content": [generated_content]
    }