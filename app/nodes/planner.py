from app.state import BlogState
from app.schemas import BlogPlan, BlogSection


def blog_planner(state: BlogState):

    analysis = state["analysis"]

    print("\nCreating blog plan...")
    print(f"Topic: {analysis.topic}")

    plan = BlogPlan(
        title="Retrieval-Augmented Generation (RAG): A Beginner's Guide",

        introduction=(
            "Introduce RAG and explain why combining retrieval "
            "with language models is useful."
        ),

        sections=[
            BlogSection(
                title="What is RAG?",
                description=(
                    "Explain Retrieval-Augmented Generation "
                    "in simple terms."
                ),
                needs_code=False,
                needs_image=True,
            ),

            BlogSection(
                title="How RAG Works",
                description=(
                    "Explain the retrieval, context augmentation, "
                    "and generation pipeline."
                ),
                needs_code=False,
                needs_image=True,
            ),

            BlogSection(
                title="Building a Simple RAG System with Python",
                description=(
                    "Show how to build a basic RAG pipeline using Python."
                ),
                needs_code=True,
                needs_image=False,
            ),

            BlogSection(
                title="Advantages and Limitations",
                description=(
                    "Discuss the main benefits and challenges of RAG."
                ),
                needs_code=False,
                needs_image=False,
            ),
        ],

        conclusion=(
            "Summarize the main ideas and explain when RAG "
            "is useful."
        ),
    )

    return {
        "plan": plan
    }