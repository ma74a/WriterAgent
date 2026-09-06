from langchain_core.messages import SystemMessage, HumanMessage
from app.llm import llm
from app.schemas import GeneratedCode, BlogSection
from app.state import BlogState


code_llm = llm.with_structured_output(
    GeneratedCode
)

def generate_code(
        section: BlogSection,
        topic: str,
        audience: str
    ):
    system_prompt = """
        You are an expert software engineer working as the
        Code Generator for an AI Writer Agent.

        Your job is to create high-quality, runnable code examples
        for technical blog posts.

        Requirements:

        - Generate code appropriate for the target audience.
        - Keep the example focused on the section.
        - Prefer simple, readable implementations.
        - Include all necessary imports.
        - Use realistic APIs and libraries.
        - Do not invent nonexistent functions or APIs.
        - Make the code as runnable as reasonably possible.
        - List required external dependencies.
        - Explain briefly what the code demonstrates in just comment.

        Return only the structured code result.
        """
    user_prompt = f"""
        Blog topic:
        {topic}

        Target audience:
        {audience}

        Section:
        {section.title}

        Section description:
        {section.description}

        Generate a practical code example for this section.
        """

    result = code_llm.invoke([
        HumanMessage(content=user_prompt),
        SystemMessage(content=system_prompt)
    ])

    return result


def code_generator(state: BlogState):
    analysis = state["analysis"]
    plan = state["plan"]

    generated_code = {}
    for section in plan.sections:
        if not section.needs_code:
            continue
        print(f"\nGenerating code: {section.title}")
        result = generate_code(
            section=section,
            topic=analysis.topic,
            audience=analysis.audience
        )

        generated_code[section.title] = result

    return {
        "code": generated_code
    }