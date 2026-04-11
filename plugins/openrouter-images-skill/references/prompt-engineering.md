# Prompt Engineering Reference

> Load this on-demand when constructing prompts for image generation.

## The 5-Component Formula

Build prompts using: **Subject → Action → Location/Context → Composition → Style**

### Component Breakdown

1. **Subject**: What is the main subject? (age, appearance, expression)
2. **Action**: What are they doing?
3. **Location/Context**: Where is the scene? Time of day?
4. **Composition**: Camera angle, framing, distance
5. **Style**: Lighting, mood, reference to prestigious contexts

## Prompt Templates

### Photorealistic / Ads
```
[Subject: age + appearance + expression], wearing [outfit with brand/texture],
[action verb] in [specific location + time]. [Micro-detail]. Captured with
[camera model], [focal length] lens at [f-stop], [lighting description].
[Prestigious context reference].
```

### Product / Commercial
```
[Product with brand name] with [dynamic element], [product detail: "logo prominently displayed"],
[surface/setting description]. [Supporting visual elements]. Commercial photography
for an advertising campaign. [Publication reference].
```

### Illustrated / Stylized
```
A [art style] [format] of [subject with character detail], featuring
[distinctive characteristics] with [color palette]. [Line style] and
[shading technique]. Background is [description]. [Mood/atmosphere].
```

## CRITICAL RULES

- **NEVER** use banned keywords: "8K", "masterpiece", "ultra-realistic" -- use `imageSize` param instead
- Name real cameras: "Sony A7R IV", "Canon EOS R5", "iPhone 16 Pro Max"
- Name real brands for styling: "Lululemon", "Tom Ford"
- Use prestigious context anchors: "Vanity Fair editorial", "National Geographic cover"
- For critical constraints use ALL CAPS: "MUST contain exactly three figures"

## Domain Modes

| Mode | When to use |
|------|-------------|
| **Cinema** | Dramatic scenes, storytelling |
| **Product** | E-commerce, packshots |
| **Portrait** | People, characters |
| **Editorial** | Fashion, lifestyle |
| **UI/Web** | Icons, illustrations |
| **Logo** | Branding, identity |
| **Landscape** | Backgrounds, wallpapers |
| **Abstract** | Patterns, textures |
| **Infographic** | Data visualization |

## Banned Keywords

These keywords actively degrade output quality:
- "8K", "4K" (in prompt - use imageSize parameter)
- "masterpiece"
- "ultra-realistic"
- "high resolution"

Use prestigious context anchors instead of quality keywords.

## Safety Rephrase Strategies

If a prompt is blocked:
1. Use abstraction: "a friendly golden retriever" instead of "dog"
2. Artistic framing: "in the style of a painting" 
3. Metaphor: "a warrior-like figure" instead of explicit content

## Best Practices

- Be SPECIFIC and VISCERAL - describe what the camera sees
- Include micro-details: "sweat droplets", "baby hairs", "texture"
- Describe the SCENE, not the concept: NOT "a dark-themed ad" but the actual scene
- Use ALL CAPS for critical constraints
