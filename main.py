from app.graph import build_graph

app = build_graph()

user_prompt = """
Write a beginner-friendly blog post explaining
Retrieval-Augmented Generation with Python examples.
Include diagrams and make it around 1500 words.
"""

result = app.invoke({"user_prompt": user_prompt})

print(result)