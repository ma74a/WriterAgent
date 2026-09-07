import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, START, END
from app.state import BlogState
from app.nodes.analyzer import prompt_analyzer
from app.nodes.researcher import web_searcher
from app.nodes.planner import blog_planner
from app.nodes.content import content_generator
from app.nodes.code import code_generator
from app.nodes.images import image_handler
from app.nodes.assembler import blog_assembler

from langgraph.constants import Send

def dispatch_parallel(state: BlogState):
    return [
        Send("content_generator", state),
        Send("code_generator", state),
        Send("image_handler", state),
    ]



def build_graph():
    graph = StateGraph(BlogState)

    graph.add_node("prompt_analyzer", prompt_analyzer)
    graph.add_node("web_searcher", web_searcher)
    graph.add_node("blog_planner", blog_planner)
    graph.add_node("content_generator", content_generator)
    graph.add_node("code_generator", code_generator)
    graph.add_node("image_handler", image_handler)
    graph.add_node("blog_assembler", blog_assembler)
    
    graph.add_edge(START, "prompt_analyzer")
    # graph.add_edge("prompt_analyzer", "web_searcher")
    # graph.add_edge("web_searcher", "blog_planner")
    graph.add_edge("prompt_analyzer", "blog_planner")
    graph.add_edge("blog_planner", "web_searcher")

    # graph.add_edge("blog_planner", "content_generator")
    # graph.add_edge("blog_planner", "code_generator")
    # graph.add_edge("blog_planner", "image_handler")
    # Conditional edge routing via Send
    graph.add_conditional_edges(
        "blog_planner",
        dispatch_parallel,
        ["content_generator", "code_generator", "image_handler"]
    )
    graph.add_edge("content_generator", "blog_assembler")
    graph.add_edge("code_generator", "blog_assembler")
    graph.add_edge("image_handler", "blog_assembler")
    graph.add_edge("blog_assembler", END)

    workflow = graph.compile()
    # png_data = workflow.get_graph().draw_mermaid_png()
    # with open("graph_parallelly_with_assembler_and_web_searcher.png", "wb") as f:
    #     f.write(png_data)

    return workflow


# build_graph()