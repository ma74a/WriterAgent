from app.graph import build_graph
from app.output import save_html, save_markdown

app = build_graph()


user_prompt = """
Write a technical but beginner-friendly blog post explaining
how to build a YOLO project using python.

Include practical code examples, explain the architecture,
and include diagrams where useful.

The article should be approximately 2000 words.
"""


result = app.invoke({
    "user_prompt": user_prompt
})


save_markdown(
    content=result["final_blog"]
)
save_html(
    content=result["final_blog"]
)