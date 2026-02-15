"""
Prompt templates for the 3-stage transformation process.
All prompts in one place so they're easy to find and tweak.
"""


class PromptTemplates:
    """All the prompts we use for DNA extraction, rulebook building, and story generation"""
    
    @staticmethod
    def dna_extraction(story: str) -> str:
        """
        Prompt for pulling out the core story elements that can work in any setting.
        Took a few tries to get this right - the key was emphasizing ABSTRACT multiple times.
        """
        return f"""Analyze this story and extract its core DNA - the portable essence that can travel to any world.

Story:
{story}

Extract the following in JSON format:

1. themes: 3-5 ABSTRACT, UNIVERSAL themes (not setting-specific)
   Example: "duty vs personal desire" NOT "ancient Indian values"
   ^ This example really helps guide the LLM

2. characters: Array of main characters with:
   - name: Character name
   - archetype: Universal role (hero, antagonist, mentor, etc.)
   - core_trait: ONE defining characteristic
   - role: Function in story

3. plot_beats: 5-7 key story moments with:
   - beat_name: Short name (e.g., "exile", "abduction")
   - description: What happens (abstract, no specific setting)
   - emotion: Primary emotion of this beat
   - act: Act number (1, 2, or 3)

4. emotional_arc: Overall emotional journey in one sentence

5. conflict_type: Core type of conflict (person vs person, person vs self, etc.)

CRITICAL: Be ABSTRACT. Focus on patterns that work in ANY setting.
Avoid culture-specific or setting-specific language.

Return ONLY valid JSON matching this structure."""

    @staticmethod
    def rulebook_building(dna_json: str, target_world: str, themes: list) -> str:
        """
        Prompt for creating the transformation rules - how old world maps to new.
        Important: need to be very explicit about preserving core traits.
        """
        return f"""Given this story DNA and target world, create a comprehensive transformation rulebook.

Story DNA:
{dna_json}

Target World: {target_world}

Create a transformation rulebook in JSON format:

1. world_setting: Dictionary with keys:
   - time_period: When this takes place
   - location: Where this takes place
   - technology_level: What tech exists
   - power_structure: Who has power and how
   - society_type: Type of society

2. character_mappings: Array mapping each original character with:
   - original: Original character name
   - new_world: NEW name appropriate for target world
   - role: Their role in new world
   - trait_preserved: Core trait that carries over

3. plot_translations: Dictionary mapping each plot beat to new world equivalent
   Keys: beat names from DNA
   Values: How this translates to new world

4. constraints: Array of 5-7 HARD RULES that MUST be followed:
   - Rules about what can/cannot appear
   - Technology limitations
   - Character name usage
   - Setting requirements

5. forbidden_elements: Array of elements that CANNOT appear (e.g., "magic" in tech world)

IMPORTANT:
- Character mappings must be CREATIVE and world-appropriate
- Preserve core themes: {', '.join(themes)}
- Be specific with constraints - these will be validated
- Make the world feel coherent and realistic

Return ONLY valid JSON."""

    @staticmethod
    def scene_generation(
        scene_num: int,
        beat: dict,
        world_setting: dict,
        character_mappings: list,
        plot_translation: str,
        constraints: list,
        forbidden: list,
        context: str,
        theme: str
    ) -> str:
        """Prompt for actually writing a scene - includes all the rules to follow"""
        char_names = "\n".join([
            f"- {m['original']} is now called: {m['new_world']} ({m['role']})" 
            for m in character_mappings
        ])
        
        return f"""Write Scene {scene_num} for our cyberpunk transformation of the Ramayana.

PLOT BEAT: {beat['beat_name']}
Description: {beat['description']}
Target Emotion: {beat.get('emotion', 'intense')}
Act: {beat.get('act', 1)}

WORLD SETTING (MUST FOLLOW):
{world_setting}

CHARACTER NAMES (USE THESE ONLY, NEVER USE ORIGINALS):
{char_names}

PLOT TRANSLATION:
{plot_translation}

HARD CONSTRAINTS (MUST FOLLOW):
{chr(10).join(f"- {c}" for c in constraints)}

FORBIDDEN (NEVER USE):
{chr(10).join(f"- {f}" for f in forbidden)}

PREVIOUS CONTEXT:
{context}

REQUIREMENTS:
- Write 350-450 words
- Use vivid, engaging prose
- Show character emotions and motivations
- Ground everything in the 2045 tech world
- Maintain theme: {theme}
- Use ONLY the new character names provided above
- NO supernatural elements - only technology
- Make it feel like a natural continuation

Write the scene now:"""

    @staticmethod
    def constraint_correction(base_prompt: str, violations: list) -> str:
        """
        When the LLM breaks rules, this enhances the prompt with specific corrections.
        Basically tells it "you messed up in these specific ways, fix them."
        """
        violation_details = "\n".join([
            f"- {v['detail']}. {v.get('suggestion', '')}" 
            for v in violations
        ])
        
        return f"""{base_prompt}

CRITICAL CORRECTIONS NEEDED:
Your previous attempt had these violations that MUST be fixed:

{violation_details}

Please regenerate the scene fixing ALL the above issues while maintaining:
- Narrative quality and engagement
- Character development
- Plot progression
- Emotional impact

Do NOT:
- Use original character names
- Reference forbidden elements
- Include supernatural/mystical elements
- Ignore world constraints"""
