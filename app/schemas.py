from pydantic import BaseModel, Field


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

class BlogPlan(BaseModel):
    """tells us HOW we'll structure the blog"""
    title: str = Field(description="The proposed blog title")
    introduction: str = Field(description="What the introduction should cover")
    sections: list[BlogSection] = Field(description="The sections that make up the blog")
    conclusion: str = Field(description="What the conclusion should cover")