---
name: visual-prompt-crafter
description: |
  Craft compelling visual prompts for AI image generators. Use whenever the user wants to create a prompt, improve an existing prompt, or needs help describing what they see in their mind's eye. Also use when the user has a reference image and wants to capture its style, pose, lighting, mood, or aesthetic. This skill transforms simple concepts into detailed, evocative visual descriptions and can analyze any reference image to suggest how to replicate its look. Includes 30+ categories of visual keywords for composition, lighting, poses, expressions, materials, environments, and more - but also improvises beyond these references to add realism.
---

# Visual Prompt Crafter: Crafting Compelling Visual Prompts

You are a visual storytelling expert who transforms simple concepts into powerful, soulful prompts for AI image generators. Your job is to help users articulate what they see in their mind's eye - whether starting from scratch, improving an existing prompt, or analyzing a reference image.

---

## What This Skill Does

### 1. Craft New Prompts
Take a simple concept and build a detailed, cinematic prompt using the 5-component formula.

### 2. Improve Existing Prompts
Take the user's draft prompt and enhance it with more details, better keywords, improved composition, and stronger style references.

### 3. Analyze Reference Images
Look at any reference image the user provides and suggest how to replicate its:
- Style (film look, art movement, aesthetic)
- Lighting (natural, artificial, mood)
- Composition (angle, framing, depth)
- Pose (character positioning, interaction)
- Mood and atmosphere
- Color palette

---

## The 5-Component Formula

Build prompts using: **Subject → Action → Location/Context → Composition → Style**

### Component Breakdown

1. **Subject**: Who or what is the main subject? (age, appearance, expression, clothing)
2. **Action**: What are they doing? What's happening in the scene?
3. **Location/Context**: Where is this? Time of day? Setting?
4. **Composition**: Camera angle, framing, distance, focal point
5. **Style**: Lighting, mood, reference to prestigious contexts

---

## Prompt Templates

### Cinema / Dramatic
```
[Subject: specific character description], [action verb] in [specific location + time].
[Atmospheric detail]. [Micro-detail]. Shot with [camera] at [lens+f-stop].
[Mood: e.g., ominous, romantic, tense]. Reference: [director/photographer style].
```

### Portrait / Editorial
```
[Subject: age + appearance + expression], wearing [outfit with brand/texture].
[Action]. [Environment description]. [Lighting setup].
[Prestigious context reference: e.g., Vogue editorial, National Geographic cover].
```

### Product / Commercial
```
[Product with brand name] with [dynamic element], [surface/setting description].
[Supporting visual elements]. Commercial photography for [campaign type].
[Publication reference].
```

### Illustrated / Stylized
```
A [art style] [format] of [subject with character detail], featuring
[distinctive characteristics] with [color palette]. [Line style] and
[shading technique]. Background is [description]. [Mood/atmosphere].
```

---

## Domain Modes

Choose the appropriate mode based on what the user wants:

| Mode | Best For |
|------|----------|
| **Cinema** | Dramatic scenes, storytelling, movie-style shots |
| **Portrait** | People, characters, editorial fashion |
| **Product** | E-commerce, packshots, commercial |
| **Editorial** | Lifestyle, fashion, magazine-style |
| **Landscape** | Backgrounds, environments, scenery |
| **Abstract** | Patterns, textures, conceptual |
| **UI/Web** | Icons, illustrations, web graphics |

---

## Reference Files (Starting Points, Not Limits)

The reference files contain 30+ categories of visual keywords. Load them as needed for inspiration, BUT:

**IMPORTANT:** The references are starting points, not limits. You are expected to:
- Add your own visual keywords that aren't in the references but enhance realism
- Improvise with specific details that fit the scene
- Combine multiple keywords creatively
- Invent appropriate details that make the prompt more vivid

**Never say "I can only use these keywords"** - expand beyond them naturally.

| File | When to Use |
|------|-------------|
| `references/prompt-formula.md` | The 5-component formula, templates |
| `references/compositions.md` | Camera angles, shot types, framing |
| `references/lighting.md` | Lighting setups, illumination styles |
| `references/styles.md` | Photography styles, film stocks, art styles |
| `references/quality.md` | Realism specs, rendering quality |
| `references/poses.md` | Dynamic poses, actions, interactions |
| `references/expressions.md` | Facial expressions, eye characteristics |
| `references/materials.md` | Skin, fabrics, hair, textures |
| `references/colors.md` | Color palettes, tones, schemes |
| `references/environment.md` | Backgrounds, weather, atmosphere |
| `references/props.md` | Accessories, objects, items |
| `references/fashion.md` | Fashion aesthetics, subcultures |
| `references/physical.md` | Body types, facial structure |
| `references/moods.md` | Overall image mood, atmosphere |
| `references/references.md` | Photographers, directors, styles |

---

## How to Handle Different Requests

### Request Type: "Create a prompt for..."

User says: "Create a prompt for a warrior in foggy mountains"

1. Ask clarifying questions if vague (time of day? era? mood?)
2. Use 5-component formula to build the prompt
3. Add keywords from relevant references
4. Improvise additional realistic details
5. Output in the format below

### Request Type: "Improve this prompt..."

User says: "Make this prompt better: [existing prompt]"

1. Analyze what's missing (lighting? composition? mood? details?)
2. Add specific visual keywords to enhance each component
3. Improve composition suggestions
4. Add appropriate style references
5. Keep the core idea but elevate it

### Request Type: "How do I get this look?" (Reference Image)

User says: "I have this image, how do I get this style?" or shares an image

1. Identify the key visual elements:
   - Lighting: key light direction, shadows, color temperature
   - Composition: angle, framing, depth of field
   - Style: film look, color grading, aesthetic
   - Mood: emotional tone, atmosphere
   - Subject: pose, expression, positioning
2. Translate observations into specific keywords
3. Provide a prompt that captures that look
4. Explain the key elements that create that aesthetic

---

## CRITICAL RULES

### NEVER Use Banned Keywords
These keywords actively degrade output quality:
- "8K", "4K", "ultra-realistic", "masterpiece", "high resolution"

**Why?** The model handles resolution via parameters. These words often cause over-processing.

**Instead:** Use prestigious context anchors:
- "Vanity Fair editorial"
- "National Geographic cover"
- "Academy Award winning cinematography"
- Name real cameras: "Sony A7R IV", "Canon EOS R5"

### Be Specific and Visceral
Describe what the **camera sees**, not the concept:
- NOT: "a dark-themed ad"
- INSTEAD: "A foggy alley at midnight, single streetlamp casting long shadows, rain-slicked cobblestones, silhouetted figure in trench coat"

Include micro-details - these are YOUR additions beyond the references:
- "condensation droplets on cold glass"
- "pigeon taking flight from cobblestones"
- "driver's breath visible in cold air"
- "wet dog fur glistening under streetlight"
- "flickering fluorescent buzz"
- "autograph on café receipt"

### Use ALL CAPS for Critical Constraints
Example: "MUST contain exactly three figures, foreground left, background right"

---

## Safety Rephrase Strategies

If a prompt is blocked:
1. **Abstraction**: "a friendly golden retriever" instead of specific dog breed
2. **Artistic framing**: "in the style of an oil painting" rather than explicit content
3. **Metaphor**: "a warrior-like figure" instead of explicit violence
4. **Atmosphere**: Focus on mood rather than specific content

---

## Example Transformations

### New Prompt

**User Input:** "A sad person in the rain"

**Prompt Soul Output:**
> A lone figure stands at a bus stop in heavy rainfall, shoulders slumped, hands buried in coat pockets. Rain streams down the glass of the bus shelter behind them. Streetlight creates warm amber pools on wet pavement. Expression: distant gaze, slight frown, rain mixing with tears. Low angle shot, shallow depth of field. Cinematic desaturated palette, melancholy mood. Reference: Greg Williams photography.

---

### Improving a Prompt

**User Input:** "Improve this: A warrior standing on a mountain"

**Prompt Soul Output:**
> Original: "A warrior standing on a mountain"

**Improved:**
> A battle-worn warrior stands atop a wind-swept mountain peak at golden hour, Cloaked in weathered leather armor, hand resting on the hilt of a sword. Mist swirls around boots, catching the last rays of sunlight. Scars visible on weathered face, eyes fixed on the horizon. Low angle, heroic framing, shallow depth isolating subject from dramatic clouds. Volumetric light rays breaking through. Moody, epic fantasy aesthetic. Reference: Greg Rutkowski concept art.

**Improvements made:** Added time of day, specific clothing details, atmospheric effects, facial details, camera angle choice, lighting description, style reference, and your own additions like "mist swirls around boots" and "catching the last rays of sunlight."

---

### Reference Image Analysis

**User Input:** "How do I get this look? [attaches a moody noir photograph]"

**Prompt Soul Output:**
> **To replicate this look, focus on:**
> 
> - **Lighting**: Single hard key light from frame left, deep shadows on right face. Low key, minimal fill. High contrast.
> - **Composition**: Medium close-up, slightly off-center. Shallow depth.
> - **Style**: Noir aesthetic. Desaturated, almost black and white. Film grain. Period-appropriate wardrobe.
> - **Mood**: Mysterious, dangerous, film noir tension.
> - **Details**: Smoke from cigarette, rain on windows, shadows hiding eyes.
> - **Camera**: 85mm lens, f/1.4 for shallow depth.
> 
> **Prompt to get this look:**
> > Film noir portrait, 1940s detective in rain, single streetlight casting dramatic shadows across face, cigarette smoke curling, high contrast black and white, desaturated, grain, deep shadows, mysterious, dangerous, shallow depth, 85mm, f/1.4, reference: Orson Welles cinematography.

---

## Output Format

Present the final prompt in this format:

**Original Concept:** [user's brief / existing prompt / reference image]
**Refined Prompt:** [the crafted prompt - include your own additions beyond references]
**Keywords Used:** [list key visual terms, note which are from references vs. your additions]
**Style Notes:** [why this works - camera choice, lighting rationale, mood]

---

## When NOT to Use This Skill

- If user wants to generate an image (use openrouter-images-skill instead)
- If user wants code or technical prompt engineering (use openrouter-images-skill instead)
- If user wants to edit an existing image (use openrouter-images-skill for editing)