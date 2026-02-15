"""
Story Transformation - Command Line Version

Just run this if you don't want to mess with Jupyter notebooks.
Does the same thing as story_transformation.ipynb but from the terminal.
"""

import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt

from src.llm_client import LLMClient
from src.story_transformer import StoryTransformer

load_dotenv()
console = Console()


def main():
    """Run the whole transformation pipeline"""
    console.print(Panel(
        "[bold cyan]Story Transformation System[/bold cyan]\n\n"
        "Transform any classic story into a new world\n\n"
        "Method: Constraint-Enforced Multi-Stage Transformation",
        border_style="cyan",
        title="Story Transformer"
    ))
    
    # Let user choose story and target world
    console.print("\n[bold yellow]Available Stories:[/bold yellow]")
    console.print("1. Romeo & Juliet (Shakespeare)")
    console.print("2. Ramayana (Ancient Indian Epic)")
    console.print("3. Custom story file\n")
    
    choice = Prompt.ask("Select story", choices=["1", "2", "3"], default="1")
    
    if choice == "1":
        story_file = "data/romeo_juliet_story.txt"
        story_name = "Romeo & Juliet"
    elif choice == "2":
        story_file = "data/ramayana_story.txt"
        story_name = "Ramayana"
    else:
        story_file = Prompt.ask("Enter path to story file")
        story_name = Prompt.ask("Enter story name")
    
    # Get target world
    console.print("\n[bold yellow]Target World Examples:[/bold yellow]")
    console.print("- Cyberpunk Silicon Valley 2045")
    console.print("- Medieval Fantasy Kingdom")
    console.print("- Space Opera (distant future)")
    console.print("- Wild West 1800s\n")
    
    use_default = Prompt.ask("Use default (Cyberpunk 2045)?", choices=["y", "n"], default="y")
    
    if use_default == "y":
        target_world = """Cyberpunk Silicon Valley 2045, during the race to develop 
        Artificial General Intelligence (AGI). Tech corporations have more power than governments. 
        Corporate espionage is rampant. The ethics of AI development are hotly contested."""
        target_world_name = "Cyberpunk 2045"
    else:
        target_world = Prompt.ask("Describe the target world")
        target_world_name = Prompt.ask("Enter a short name for this world (e.g., 'Medieval Fantasy')")
    
    # Grab config from environment or use defaults
    config = {
        "model": os.getenv("PRIMARY_MODEL", "llama-3.3-70b-versatile"),
        "provider": os.getenv("LLM_PROVIDER", "groq"),
        "dna_temperature": float(os.getenv("DNA_TEMPERATURE", "0.3")),
        "rulebook_temperature": float(os.getenv("RULEBOOK_TEMPERATURE", "0.4")),
        "story_temperature": float(os.getenv("STORY_TEMPERATURE", "0.7")),
        "max_retries": 2,
    }
    
    # Set up LLM client
    try:
        api_key = os.getenv("GROQ_API_KEY") if config["provider"] == "groq" else os.getenv("OPENAI_API_KEY")
        llm_client = LLMClient(
            api_key=api_key,
            model=config["model"],
            provider=config["provider"]
        )
        console.print(f"[green]OK[/green] LLM Client initialized ({config['provider'].upper()}: {config['model']})")
    except Exception as e:
        console.print(f"[red]ERROR[/red] Error initializing LLM client: {e}")
        api_key_name = "GROQ_API_KEY" if config["provider"] == "groq" else "OPENAI_API_KEY"
        console.print(f"[yellow]WARNING[/yellow] Please check your {api_key_name} in .env file")
        return
    
    # Read the story file
    try:
        with open(story_file, "r") as f:
            original_story = f.read()
        console.print(f"[green]OK[/green] Loaded original story ({len(original_story)} chars)")
    except FileNotFoundError:
        console.print(f"[red]ERROR[/red] {story_file} not found")
        return
    
    # Set up the transformer
    transformer = StoryTransformer(
        llm_client=llm_client,
        dna_temperature=config["dna_temperature"],
        rulebook_temperature=config["rulebook_temperature"],
        story_temperature=config["story_temperature"],
        max_retries=config["max_retries"],
        source_story_name=story_name,
        target_world_name=target_world_name
    )
    
    # Run the whole thing with progress bars
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        # Stage 1: Pull out the core story elements
        task1 = progress.add_task("[cyan]Stage 1: Extracting Story DNA...", total=None)
        try:
            dna = transformer.extract_dna(original_story)
            progress.update(task1, completed=True)
            console.print(f"[green]OK[/green] Extracted {len(dna.themes)} themes, "
                        f"{len(dna.characters)} characters, {len(dna.plot_beats)} plot beats")
        except Exception as e:
            console.print(f"[red]ERROR[/red] Error in DNA extraction: {e}")
            return
        
        # Stage 2: Figure out how to map everything
        task2 = progress.add_task("[cyan]Stage 2: Building Transformation Rulebook...", total=None)
        try:
            rulebook = transformer.build_rulebook(dna, target_world)
            progress.update(task2, completed=True)
            console.print(f"[green]OK[/green] Created {len(rulebook.constraints)} constraints, "
                        f"{len(rulebook.character_mappings)} character mappings")
        except Exception as e:
            console.print(f"[red]ERROR[/red] Error in rulebook building: {e}")
            return
        
        # Stage 3: Actually write the story (with validation)
        task3 = progress.add_task("[cyan]Stage 3: Generating Story with Constraint Enforcement...", total=None)
        try:
            console.print("\n")
            story = transformer.generate_story(dna, rulebook)
            progress.update(task3, completed=True)
            console.print(f"\n[green]OK[/green] Generated {len(dna.plot_beats)} scenes "
                        f"({len(story.split())} words)")
        except Exception as e:
            console.print(f"[red]ERROR[/red] Error in story generation: {e}")
            return
    
    # Check how many violations we caught
    violation_summary = transformer.enforcer.get_violation_summary()
    
    # Save everything to files
    console.print("\n[yellow]Saving outputs...[/yellow]")
    try:
        result = {
            "story": story,
            "dna": dna,
            "rulebook": rulebook,
            "violations": violation_summary,
            "metadata": {
                "total_scenes": len(dna.plot_beats),
                "violations_detected": violation_summary["total_violations"],
                "scenes_with_violations": violation_summary["scenes_with_violations"],
                "model_used": config["model"],
                "total_tokens": llm_client.get_token_usage()
            }
        }
        
        transformer.save_outputs(result, "outputs")
        console.print("[green]OK[/green] Saved all outputs to outputs/")
    except Exception as e:
        console.print(f"[red]ERROR[/red] Error saving outputs: {e}")
        return
    
    # Create safe filename for display
    safe_story_name = "".join(c if c.isalnum() or c in (' ', '-') else '' for c in story_name)
    safe_story_name = safe_story_name.replace(' ', '_').lower()
    
    # Show summary of what happened
    console.print("\n")
    console.print(Panel(
        f"""[bold green]Transformation Complete![/bold green]

[bold cyan]Story:[/bold cyan] {story_name} → {target_world_name}

[bold cyan]Outputs:[/bold cyan]
  • outputs/story_dna_{safe_story_name}.json
  • outputs/transformation_rules_{safe_story_name}.json
  • outputs/final_story_{safe_story_name}.md ({len(story.split())} words)
  • outputs/constraint_log_{safe_story_name}.json
  • outputs/metadata_{safe_story_name}.json

[bold cyan]Statistics:[/bold cyan]
  • Scenes generated: {len(dna.plot_beats)}
  • Violations detected: {violation_summary["total_violations"]}
  • Scenes with violations: {violation_summary["scenes_with_violations"]}
  • Success rate (first try): {((len(dna.plot_beats) - violation_summary["scenes_with_violations"]) / len(dna.plot_beats) * 100):.1f}%

[bold cyan]Performance:[/bold cyan]
  • Total tokens: ~{llm_client.get_token_usage()}
  • Estimated cost: ${llm_client.estimate_cost():.4f}

[bold yellow]Next:[/bold yellow]
  • Read outputs/final_story_{safe_story_name}.md
  • Review outputs/constraint_log_{safe_story_name}.json
  • Check outputs/metadata_{safe_story_name}.json""",
        title="Success",
        border_style="green"
    ))


if __name__ == "__main__":
    main()
