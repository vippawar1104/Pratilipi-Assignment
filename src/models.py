"""
Data structures for story transformation.
Using Pydantic because it catches errors early and makes the data self-documenting.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class Character(BaseModel):
    """Represents a character with their core traits"""
    name: str = Field(description="Character name")
    archetype: str = Field(description="Universal role (hero, antagonist, etc.)")
    core_trait: str = Field(description="One defining characteristic")
    role: str = Field(description="Function in the story")


class PlotBeat(BaseModel):
    """A single important moment in the story"""
    beat_name: str = Field(description="Short name for this beat")
    description: str = Field(description="What happens (abstract)")
    emotion: str = Field(description="Primary emotion")
    act: int = Field(description="Act number (1, 2, or 3)")


class StoryDNA(BaseModel):
    """The core elements that make a story recognizable across any setting"""
    themes: List[str] = Field(description="3-5 abstract, universal themes")
    characters: List[Character] = Field(description="Main character archetypes")
    plot_beats: List[PlotBeat] = Field(description="5-7 key story moments")
    emotional_arc: str = Field(description="Overall emotional journey")
    conflict_type: str = Field(description="Type of core conflict")


class CharacterMapping(BaseModel):
    """How an old character becomes a new character"""
    original: str = Field(description="Original character name")
    new_world: str = Field(description="New world character name")
    role: str = Field(description="Role in new world")
    trait_preserved: str = Field(description="Core trait that carries over")


class Rulebook(BaseModel):
    """All the rules for how to transform the story into the new world"""
    world_setting: Dict[str, str] = Field(description="World parameters")
    character_mappings: List[CharacterMapping] = Field(description="Character translations")
    plot_translations: Dict[str, str] = Field(description="Plot beat translations")
    constraints: List[str] = Field(description="Hard rules that must be followed")
    forbidden_elements: List[str] = Field(description="Elements that cannot appear")


class ConstraintViolation(BaseModel):
    """When the LLM breaks one of our transformation rules"""
    type: str = Field(description="Type of violation")
    severity: str = Field(description="Severity level: low, medium, high")
    detail: str = Field(description="Description of the violation")
    suggestion: Optional[str] = Field(default=None, description="How to fix it")


class TransformationMetadata(BaseModel):
    """Stats about how the transformation went"""
    total_scenes: int
    scenes_with_violations: int
    total_violations: int
    violation_types: Dict[str, int]
    success_rate_first_try: str
    model_used: str
    total_tokens_estimated: Optional[int] = None
