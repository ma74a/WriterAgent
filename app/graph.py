from langgraph.graph import StateGraph, START, END
from app.state import BlogState
from app.nodes.analyzer import prompt_analyzer


def build_graph():
    graph = StateGraph(BlogState)

    graph.add_node("prompt_analyzer", prompt_analyzer)

    graph.add_edge(START, "prompt_analyzer")
    graph.add_edge("prompt_analyzer", END)

    return graph.compile()
