from langgraph.graph import StateGraph, START, END
from app.state import BlogState
from app.nodes.analyzer import prompt_analyzer
from app.nodes.planner import blog_planner
from app.nodes.content import content_generator


def build_graph():
    graph = StateGraph(BlogState)

    graph.add_node("prompt_analyzer", prompt_analyzer)
    graph.add_node("blog_planner", blog_planner)
    graph.add_node("content_generator", content_generator)

    graph.add_edge(START, "prompt_analyzer")
    graph.add_edge("prompt_analyzer", "blog_planner")
    graph.add_edge("blog_planner", "content_generator")
    graph.add_edge("content_generator", END)

    return graph.compile()
