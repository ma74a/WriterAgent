from pydantic import BaseModel, Field
from typing import Literal


class PromptAnalysis(BaseModel):
    """This represents the output of the Prompt Analyzer."""
    topic: str = Field(description="The main topic of the blog post")
    audience: str = Field(description="The intended target audience")
    tone: str = Field(description="The desired writing tone")
    needs_code: bool = Field(description="Whether the blog should contain code examples")
    needs_images: bool = Field(description="Whether the blog should contain images or diagrams")
    word_count: int = Field(description="Approximate desired word count")

class BlogSection(BaseModel):
    title: str = Field(description="Section title")
    description: str = Field(description="What this section should explain")
    needs_code: bool = Field(description="Whether this section needs code")
    needs_image: bool = Field(description="Whether this section needs an image or diagram")
    image_type: Literal["photo", "diagram"] = "photo"

class BlogPlan(BaseModel):
    """tells us HOW we'll structure the blog"""
    title: str = Field(description="The proposed blog title")
    introduction: str = Field(description="What the introduction should cover")
    sections: list[BlogSection] = Field(description="The sections that make up the blog")
    conclusion: str = Field(description="What the conclusion should cover")

class GeneratedSection(BaseModel):
    title: str = Field(description="The title of generated Section")
    content: str = Field(description="The content of the generated section")

class GeneratedCode(BaseModel):
    section_title: str = Field(description="The blog section this code belongs to")
    language: str = Field(description="Programming language used by the code")
    explanation: str = Field(description="Short explanation of what the code demonstrates")
    dependencies: list[str] = Field(description="Packages or dependencies required to run the code")
    code: str = Field(description="The actual runnable code")

class ResearchSource(BaseModel):
    title: str = Field(description="Title of the web source")
    url: str = Field(description="Url of web source")
    content: str = Field(description="Relevant content returned by the search engine")
    score: float = Field(description="Relevance score returned by the search engine")


class ResearchResult(BaseModel):
    query: str = Field(description="The search query used")
    sources: list[ResearchSource] = Field(description="Sources returns by the search engine")

class ResearchContext(BaseModel):
    results: list[ResearchResult] = Field(
        description="All web research results"
    )