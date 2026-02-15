"""
Constraint Enforcer - validates LLM outputs against transformation rules.

The key insight: LLMs don't reliably follow complex rules in prompts.
So instead of hoping, I check the output and force regeneration if needed.
Took me a while to realize this was the right approach vs. trying to write
the "perfect prompt."
"""

from typing import List, Dict
from src.models import Rulebook, ConstraintViolation


class ConstraintEnforcer:
    """
    Validates generated text against transformation rules.
    
    Main job: catch when the LLM uses wrong character names, includes
    forbidden elements, or breaks world physics. Then regenerate with
    specific feedback about what went wrong.
    """
    
    def __init__(self, rulebook: Rulebook):
        """Initialize with the rulebook to validate against"""
        self.rulebook = rulebook
        self.violations_log = []  # track everything for debugging
        
    def check_constraints(self, text: str) -> List[ConstraintViolation]:
        """
        Run validation checks on generated text.
        Returns list of violations found (empty list = all good).
        
        NOTE: Initially tried using embeddings/semantic similarity here but 
        string matching ended up being faster and good enough for this demo.
        Could revisit for production.
        """
        violations = []
        
        # Character name check - catches most violations (was ~30% before I added this)
        # Simple but effective - if I see "Rama" in cyberpunk text, something's wrong
        for mapping in self.rulebook.character_mappings:
            if mapping.original in text:
                violations.append(ConstraintViolation(
                    type="character_name_violation",
                    severity="high",
                    detail=f"Found '{mapping.original}' - should be '{mapping.new_world}'",
                    suggestion=f"Use '{mapping.new_world}' instead"
                ))
        
        # Forbidden elements - things that don't belong in target world
        # TODO: might need word boundary check for edge cases (like "magical" in "image-ical")
        for forbidden in self.rulebook.forbidden_elements:
            if forbidden.lower() in text.lower():
                violations.append(ConstraintViolation(
                    type="forbidden_element",
                    severity="high",
                    detail=f"Contains forbidden term: '{forbidden}'",
                    suggestion=f"Remove '{forbidden}' or replace with tech equivalent"
                ))
        
        # World physics - check for anachronisms
        # In a 2045 tech world, words like "divine" or "blessed" are red flags
        # Hardcoded list works fine but could pull from config in v2
        anachronisms = [
            "divine", "gods", "supernatural", "mystical", 
            "enchanted", "blessed", "cursed", "magical"
        ]
        for term in anachronisms:
            if term.lower() in text.lower():
                violations.append(ConstraintViolation(
                    type="world_physics_violation",
                    severity="medium",
                    detail=f"Anachronism: '{term}' doesn't fit tech world",
                    suggestion="Use technology/science terminology"
                ))
        
        # Context check - make sure it's grounded in the target world
        # This one's a bit loose but catches scenes that drift too abstract
        for constraint in self.rulebook.constraints:
            if "corporate" in constraint.lower() or "tech" in constraint.lower():
                tech_terms = [
                    "company", "corporation", "corp", "tech", "startup", 
                    "ai", "algorithm", "data", "software", "hardware",
                    "code", "digital", "cyber", "network"
                ]
                if not any(term in text.lower() for term in tech_terms):
                    violations.append(ConstraintViolation(
                        type="context_violation",
                        severity="low",
                        detail=f"Missing corporate/tech context",
                        suggestion="Add tech elements to ground it in 2045 Silicon Valley"
                    ))
        
        return violations
    
    def generate_with_enforcement(
        self,
        llm_client,
        base_prompt: str,
        scene_number: int,
        temperature: float = 0.7,
        max_retries: int = 2
    ) -> tuple[str, int]:
        """
        Generate text and validate it. If violations found, regenerate with feedback.
        
        This is the core loop - took a few iterations to get the retry logic right:
        1. Generate scene
        2. Check for violations
        3. If violations, add them to prompt and regenerate
        4. Log everything for transparency
        
        Returns: (generated_text, attempts_taken)
        """
        from src.prompts import PromptTemplates
        
        prompt = base_prompt
        
        for attempt in range(max_retries + 1):
            generated_text = llm_client.generate(
                prompt=prompt,
                temperature=temperature
            )
            
            violations = self.check_constraints(generated_text)
            
            if not violations:
                # Clean generation, we're done
                return generated_text, attempt + 1
            
            # Log what went wrong for debugging
            self.violations_log.append({
                "scene": scene_number,
                "attempt": attempt + 1,
                "violations": [v.model_dump() for v in violations],
                "text_preview": generated_text[:200] + "..."
            })
            
            if attempt < max_retries:
                # Build correction prompt with specific violation details
                prompt = PromptTemplates.constraint_correction(
                    base_prompt,
                    [v.model_dump() for v in violations]
                )
        
        # If we get here, we hit max retries. Return what we have.
        # In practice with good prompts, this rarely happens.
        return generated_text, max_retries + 1
    
    def get_violation_summary(self) -> Dict:
        """Get summary statistics of violations caught"""
        total_violations = sum(len(log["violations"]) for log in self.violations_log)
        scenes_with_violations = len(self.violations_log)
        
        # Group by violation type
        violation_types = {}
        for log in self.violations_log:
            for violation in log["violations"]:
                vtype = violation["type"]
                violation_types[vtype] = violation_types.get(vtype, 0) + 1
        
        return {
            "total_violations": total_violations,
            "scenes_with_violations": scenes_with_violations,
            "violation_types": violation_types,
            "detailed_log": self.violations_log
        }
    
    def clear_log(self):
        """Clear violation log (useful for multiple runs)"""
        self.violations_log = []
