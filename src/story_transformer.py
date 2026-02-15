"""
Story Transformer - the main class that runs everything.

This orchestrates the whole pipeline from start to finish.
"""

import json
from typing import Dict
from src.models import StoryDNA, Rulebook, TransformationMetadata
from src.llm_client import LLMClient
from src.prompts import PromptTemplates
from src.constraint_enforcer import ConstraintEnforcer


class StoryTransformer:
    """
    Runs the 3-stage transformation process:
    Stage 1: Figure out what makes the story tick (DNA)
    Stage 2: Define how to map it to the new world (Rulebook)
    Stage 3: Actually write the new story with validation
    
    The multi-temperature strategy came from testing - 0.3/0.4/0.7 worked best.
    """
    
    def __init__(
        self, 
        llm_client: LLMClient,
        dna_temperature: float = 0.3,  # Low for consistency
        rulebook_temperature: float = 0.4,  # Balanced
        story_temperature: float = 0.7,  # Higher for creativity
        max_retries: int = 2,
        source_story_name: str = "Unknown Story",
        target_world_name: str = "2045"
    ):
        """
        Set up the transformer with different creativity levels for each stage.
        Low temp (0.3) for extraction = more factual
        Medium temp (0.4) for rules = balanced
        High temp (0.7) for writing = more creative
        """
        self.llm_client = llm_client
        self.dna_temperature = dna_temperature
        self.rulebook_temperature = rulebook_temperature
        self.story_temperature = story_temperature
        self.max_retries = max_retries
        self.source_story_name = source_story_name
        self.target_world_name = target_world_name
        
        self.story_dna = None
        self.rulebook = None
        self.enforcer = None
        
    def extract_dna(self, original_story: str) -> StoryDNA:
        """
        Stage 1: Pull out the core elements that can travel to any world.
        Things like "hero's journey" or "forbidden love" work anywhere.
        """
        prompt = PromptTemplates.dna_extraction(original_story)
        
        response = self.llm_client.generate_json(
            prompt=prompt,
            temperature=self.dna_temperature
        )
        dna_data = json.loads(response)
        self.story_dna = StoryDNA(**dna_data)
        
        return self.story_dna
    
    def build_rulebook(self, dna: StoryDNA, target_world: str) -> Rulebook:
        """
        Stage 2: Figure out how to map the old story to the new world.
        Like "kingdom" becomes "corporation" or "sword fight" becomes "legal battle".
        """
        prompt = PromptTemplates.rulebook_building(
            dna_json=dna.model_dump_json(indent=2),
            target_world=target_world,
            themes=dna.themes
        )
        
        response = self.llm_client.generate_json(
            prompt=prompt,
            temperature=self.rulebook_temperature
        )
        rulebook_data = json.loads(response)
        self.rulebook = Rulebook(**rulebook_data)
        self.enforcer = ConstraintEnforcer(self.rulebook)
        
        return self.rulebook
    
    def generate_story(self, dna: StoryDNA, rulebook: Rulebook) -> str:
        """
        Stage 3: Actually write the new story, one scene at a time.
        The constraint enforcer checks each scene to make sure it follows the rules.
        
        Context management: only pass last 2 scenes to avoid token overflow.
        Tried passing all scenes but hit limits around scene 5-6.
        """
        if not self.enforcer:
            self.enforcer = ConstraintEnforcer(rulebook)
        
        scenes = []
        
        for i, beat in enumerate(dna.plot_beats, 1):
            # Give it context from what we've written so far (last 2 scenes)
            context = "\n\n".join(scenes[-2:]) if scenes else "This is the opening scene."
            plot_translation = rulebook.plot_translations.get(
                beat.beat_name, 
                beat.description
            )
            base_prompt = PromptTemplates.scene_generation(
                scene_num=i,
                beat=beat.model_dump(),
                world_setting=rulebook.world_setting,
                character_mappings=[m.model_dump() for m in rulebook.character_mappings],
                plot_translation=plot_translation,
                constraints=rulebook.constraints,
                forbidden=rulebook.forbidden_elements,
                context=context,
                theme=dna.themes[0]
            )
            scene_text, attempts = self.enforcer.generate_with_enforcement(
                llm_client=self.llm_client,
                base_prompt=base_prompt,
                scene_number=i,
                temperature=self.story_temperature,
                max_retries=self.max_retries
            )
            
            scenes.append(scene_text)
        
        return "\n\n---\n\n".join(scenes)
    
    def transform(
        self, 
        original_story: str, 
        target_world: str
    ) -> Dict:
        """Run the full transformation from start to finish"""
        dna = self.extract_dna(original_story)
        rulebook = self.build_rulebook(dna, target_world)
        story = self.generate_story(dna, rulebook)
        violation_summary = self.enforcer.get_violation_summary()
        metadata = TransformationMetadata(
            total_scenes=len(dna.plot_beats),
            scenes_with_violations=violation_summary["scenes_with_violations"],
            total_violations=violation_summary["total_violations"],
            violation_types=violation_summary["violation_types"],
            success_rate_first_try=f"{((len(dna.plot_beats) - violation_summary['scenes_with_violations']) / len(dna.plot_beats) * 100):.1f}%",
            model_used=self.llm_client.model,
            total_tokens_estimated=self.llm_client.get_token_usage()
        )
        
        return {
            "story": story,
            "dna": dna,
            "rulebook": rulebook,
            "violations": violation_summary,
            "metadata": metadata
        }
    
    def save_outputs(self, result: Dict, output_dir: str = "outputs"):
        """Save everything to files so you can see what happened at each stage"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Create safe filename from story name (remove special chars)
        safe_story_name = "".join(c if c.isalnum() or c in (' ', '-') else '' for c in self.source_story_name)
        safe_story_name = safe_story_name.replace(' ', '_').lower()
        
        with open(f"{output_dir}/story_dna_{safe_story_name}.json", "w") as f:
            f.write(result["dna"].model_dump_json(indent=2))
        with open(f"{output_dir}/transformation_rules_{safe_story_name}.json", "w") as f:
            f.write(result["rulebook"].model_dump_json(indent=2))
        with open(f"{output_dir}/final_story_{safe_story_name}.md", "w") as f:
            f.write(f"# {self.source_story_name} {self.target_world_name}\n\n")
            f.write(f"*A transformation of the classic tale to {self.target_world_name}*\n\n")
            f.write("---\n\n")
            f.write(result["story"])
            f.write("\n\n---\n\n")
            f.write("## About This Story\n\n")
            f.write("This story was generated through a systematic 3-stage transformation pipeline:\n\n")
            f.write("1. **DNA Extraction**: Identified themes, characters, and plot structure\n")
            f.write("2. **Rulebook Building**: Created transformation rules for the target world\n")
            f.write("3. **Constrained Generation**: Generated with active validation\n\n")
            f.write(f"**Themes preserved**: {', '.join(result['dna'].themes)}\n\n")
            f.write(f"**Innovation**: Constraint Enforcer detected and corrected {result['violations']['total_violations']} violations\n")
        with open(f"{output_dir}/constraint_log_{safe_story_name}.json", "w") as f:
            json.dump(result["violations"], f, indent=2)
        with open(f"{output_dir}/metadata_{safe_story_name}.json", "w") as f:
            metadata = result["metadata"]
            if hasattr(metadata, 'model_dump_json'):
                f.write(metadata.model_dump_json(indent=2))
            else:
                json.dump(metadata, f, indent=2)
