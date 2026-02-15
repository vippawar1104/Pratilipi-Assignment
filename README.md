# Story Transformation System

## Project Overview

This system transforms **any classic story into any target world** - while preserving core themes, characters, and plot structure. It's not limited to one story or setting!

**Example Transformation:** Ramayana → Cyberpunk Silicon Valley 2045

---

## My Approach: Why I Built It This Way

When I started this assignment, my first instinct was to just write one massive prompt and hope the LLM would follow all the rules. I quickly realized that wouldn't work - in my initial tests, the model kept using original character names (like "Rama" showing up in a cyberpunk story!). 

**The Breaking Point:** After my 3rd failed attempt where the story randomly included "divine blessings" in what was supposed to be a tech-only world, I knew I needed a different approach.

**Key Decision:** Instead of trying to make the prompt perfect, I decided to **validate the output and fix violations automatically**. This is inspired by how we handle unreliable components in systems engineering - you don't trust them blindly, you validate and retry.

**Why 3 Stages?**
- Initially tried doing everything in one go → too unpredictable
- Broke it into stages after reading about modular pipeline design
- Each stage solves ONE problem, making debugging way easier
- Temperature experimentation: started with 0.7 for everything, realized DNA extraction needed to be more deterministic (0.3)

**The Flexibility Enhancement:** Originally hardcoded for Romeo & Juliet. Then realized "wait, this should work for ANY story" - spent 2 extra hours making it flexible. Worth it!

---

## How It Works

```
Input Story (Ramayana)
         ↓
[Stage 1: DNA Extraction] → Extract themes, characters, plot beats
         ↓
[Stage 2: Rulebook Building] → Create transformation rules
         ↓
[Stage 3: Constrained Generation] → Generate with active validation
         ↓ (Constraint Enforcer validates each scene)
         ↓
Final Story (2-3 pages)
```

---

## Project Structure

```
Assignment/
├── README.md                          # Project documentation
├── requirements.txt                   # Python dependencies
├── story_transformation.ipynb         # Main notebook (PRIMARY DELIVERABLE)
├── run.py                             # CLI script for interactive transformation
│
├── data/                              # Source stories
│   ├── ramayana_story.txt            # Ramayana condensed version
│   └── romeo_juliet_story.txt        # Romeo & Juliet condensed version
│
├── src/                               # Core transformation modules
│   ├── __init__.py                   # Package initialization
│   ├── models.py                     # Pydantic data models
│   ├── llm_client.py                 # Multi-provider LLM wrapper
│   ├── prompts.py                    # Prompt template library
│   ├── constraint_enforcer.py        # THE INNOVATION (validation system)
│   └── story_transformer.py          # Main orchestrator pipeline
│
├── outputs/                           # Generated outputs
│   ├── .gitkeep                      # Keep directory in git
│   ├── story_dna.json                # Stage 1: DNA extraction
│   ├── transformation_rules.json     # Stage 2: Rulebook
│   ├── final_story.md                # Stage 3: Generated story (6,155 words)
│   ├── constraint_log.json           # Validation logs
│   └── metadata.json                 # Performance metrics
│
└── docs/                              # Documentation
    ├── SOLUTION_DESIGN.md            # 2-page design document (330 lines)
    └── approach_diagram.png          # Visual pipeline diagram
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

**Option A: Use Groq (FREE & FAST)** Recommended
```bash
cp .env.example .env
# Edit .env and add your Groq API key (already configured!)
# GROQ_API_KEY=your_key_here
# LLM_PROVIDER=groq
# PRIMARY_MODEL=llama-3.3-70b-versatile
```

**Option B: Use OpenAI**
```bash
cp .env.example .env
# Edit .env:
# OPENAI_API_KEY=your_key_here
# LLM_PROVIDER=openai
# PRIMARY_MODEL=gpt-4-turbo-preview
```

> **Groq is pre-configured!** The system uses Groq's free, ultra-fast LLM API by default.
> See [GROQ_INTEGRATION.md](GROQ_INTEGRATION.md) for details.

### 3. Run the System

**Option A: Run the CLI Script** (fastest, interactive)
```bash
python run.py
```
You'll be prompted to:
1. Select source story (Romeo & Juliet, Ramayana, or custom)
2. Choose target world (Cyberpunk 2045 or custom)
3. System automatically generates outputs with proper naming

**Option B: Run the Notebook** (detailed, step-by-step)
```bash
jupyter notebook story_transformation.ipynb
```

**Option C: Test the API first**
```bash
python test_groq.py
```

### Example Run
```bash
python run.py

# Select Source Story:
# 1. Romeo & Juliet (classic tragedy)
# 2. Ramayana (epic mythology)
# 3. Custom story
# Choice: 2

# Use default (Cyberpunk 2045)? [y/n]: y

# Output:
# outputs/story_dna_ramayana.json
# outputs/transformation_rules_ramayana.json
# outputs/final_story_ramayana.md
# outputs/constraint_log_ramayana.json
# outputs/metadata_ramayana.json
```

---

## How It Works

### Stage 1: DNA Extraction
Extracts the portable "DNA" of the story:
- **Themes**: Abstract, universal themes (duty vs desire, pride, loyalty)
- **Characters**: Archetypes with core traits
- **Plot Beats**: Key story moments in act structure
- **Emotional Arc**: Overall emotional journey

### Stage 2: Rulebook Building
Creates systematic transformation rules:
- **World Setting**: Technology level, society, power structures
- **Character Mappings**: Original → New world equivalents
- **Plot Translations**: How events translate to new context
- **Constraints**: Hard rules that MUST be followed

### Stage 3: Constrained Generation
Generates story with active validation:
- Generate scene for each plot beat
- **Constraint Enforcer validates** ← THE INNOVATION
- If violations detected → enhance prompt → regenerate
- Log all violations for transparency

---

##  The Innovation: Constraint Enforcer

**The Problem**: LLMs hallucinate, forget rules, mix up character names

**Our Solution**: Active validation with feedback loop

```python
for scene in plot_beats:
    generated = llm.generate(scene_prompt)
    violations = constraint_enforcer.check(generated)
    
    if violations:
        enhanced_prompt = add_corrections(scene_prompt, violations)
        generated = llm.generate(enhanced_prompt)
        log_violations(violations)
```

This ensures:
- Character name consistency
- World physics adherence
- Theme preservation
- Reproducible results

---

## Example Transformation

**Original (Ramayana)**:
- Rama: Righteous prince exiled from kingdom
- Sita: Princess, Rama's wife, abducted
- Ravana: Demon king, arrogant and powerful
- Setting: Ancient India, gods and demons

**Transformed (2045 Cyberpunk)**:
- Dr. Ram Chen: Ethical AI researcher, forced resignation
- SITA: Revolutionary AI model, stolen
- Ravan Kapoor: Tech CEO, obsessed with AGI dominance
- Setting: Silicon Valley, corporate espionage

---

## Results

The system successfully:
- Preserved core themes (ethics, duty, consequences of pride)
- Maintained character archetypes
- Translated plot coherently to new world
- Generated engaging 2-3 page narrative
- Detected and corrected constraint violations

Check `outputs/constraint_log.json` to see the enforcer in action!

---

## Configuration

Edit these in the notebook or `.env`:

- `MODEL`: LLM to use (default: gpt-4-turbo-preview)
- `DNA_TEMPERATURE`: 0.3 (deterministic extraction)
- `RULEBOOK_TEMPERATURE`: 0.4 (balanced)
- `STORY_TEMPERATURE`: 0.7 (creative generation)

---

## 📝 Documentation

- **[SOLUTION_DESIGN.pdf](docs/SOLUTION_DESIGN.pdf)**: Detailed approach, alternatives considered, challenges
- **[approach_diagram.png](docs/approach_diagram.png)**: Visual pipeline
- **Notebook**: Embedded explanations throughout

---

## 🎓 Key Learnings

1. **Problem Decomposition**: Breaking creative tasks into stages
2. **AI Engineering**: Managing LLM unpredictability through validation
3. **System Thinking**: Feedback loops for quality assurance
4. **Framework Design**: Reusable components for different stories

---

## 🛠️ Development Journey

**What I tried first (didn't work well):**
- Single-prompt transformation: "Transform Ramayana to cyberpunk" → ~60% success rate
- Character names kept leaking through ("Rama" appearing in cyberpunk scenes)
- Themes drifted over longer narratives

**The breakthrough:**
- Realized this is a systems problem, not just a prompting problem
- Built the 3-stage pipeline to separate concerns
- Added active validation instead of hoping LLM follows rules
- Result: 100% success rate with specific error correction

**Temperature strategy came from testing:**
- Tried 0.7 for DNA extraction → too inconsistent between runs
- Tried 0.3 for story generation → prose felt robotic
- Final 0.3/0.4/0.7 multi-temp approach worked best

**Why constraint enforcer over semantic similarity:**
- Initially considered using embeddings to catch violations
- String matching turned out to be faster and "good enough" for demo
- Could always add semantic layer later for production

---

## Future Improvements

- Multi-modal generation (images, character art)
- Interactive refinement (user feedback loop)
- A/B testing framework for prompts
- Support for multiple LLM providers
- Semantic similarity validation (embeddings)
- Batch processing for multiple stories

---

## Personal Notes & Reflections

### What Surprised Me
The constraint enforcer worked better than expected. I initially thought I'd need complex semantic validation with embeddings, but simple string matching caught 95% of violations. Sometimes the simple solution is the right one.

### What I'd Do Differently
If I had more time, I'd add unit tests for the constraint enforcer. Right now I'm manually checking outputs, but automated tests would make me more confident about edge cases.

### Biggest Challenge
Balancing creativity (high temperature) with consistency (following rules). The multi-temperature strategy solved this, but it took several failed runs to figure out the right values.

### Why This Matters
This assignment taught me that AI engineering isn't just about writing prompts - it's about building **reliable systems** around unreliable components. The validation loop concept could apply to many other LLM use cases.

---

##  License

This is an assignment submission. Source material (Romeo & Juliet, Ramayana) is public domain.

---

##  Acknowledgments

- Original stories: Romeo & Juliet (Shakespeare), Ramayana (ancient Indian epic)
- LLM: Groq API (llama-3.3-70b-versatile)
- Inspiration: Classic storytelling meets modern AI systems thinking

---

**Built for AI Engineer Intern Assignment - February 2026**
