"""
Story Transformation System - Modular Implementation

This package contains all the modular components for the story transformation system.
"""

from src.models import (
    Character,
    PlotBeat,
    StoryDNA,
    CharacterMapping,
    Rulebook,
    ConstraintViolation,
    TransformationMetadata
)

from src.llm_client import LLMClient
from src.prompts import PromptTemplates
from src.constraint_enforcer import ConstraintEnforcer
from src.story_transformer import StoryTransformer

__all__ = [
    # Data models
    'Character',
    'PlotBeat',
    'StoryDNA',
    'CharacterMapping',
    'Rulebook',
    'ConstraintViolation',
    'TransformationMetadata',
    
    # Core components
    'LLMClient',
    'PromptTemplates',
    'ConstraintEnforcer',
    'StoryTransformer',
]

__version__ = '1.0.0'
__author__ = 'AI Engineer Intern Assignment'
