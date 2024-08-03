"""Entity Relationship Description Summarization Module."""

from .prompt import DefaultSummarizeDescriptionPromptBuilder
from .summarizer import EntityRelationshipDescriptionSummarizer

__all__ = [
    "DefaultSummarizeDescriptionPromptBuilder",
    "EntityRelationshipDescriptionSummarizer",
]
