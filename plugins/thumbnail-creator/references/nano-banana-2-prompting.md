# Nano Banana 2 Prompting Reference

> Extracted from official Google guides (March 2026).
> Read this file when writing or refining image generation prompts for NB2.

---

## What is Nano Banana 2?

Nano Banana 2 = Gemini 3.1 Flash Image. It offers ~95% of Pro's capability at a fraction of the cost. **Use it as your default for all thumbnail generation.**

Step up to Nano Banana Pro only when NB2 consistently fails complex, multi-layered prompts.

---

## Tech Specs (Quick Reference)

| Feature | Nano Banana 2 | Nano Banana Pro |
|---|---|---|
| Model ID | gemini-3.1-flash-image-preview | gemini-3-pro-image |
| Input tokens | 131,072 max | 65,536 max |
| Output tokens | 32,768 max | 32,768 max |
| Resolutions | 512px, 1K, 2K, 4K | 1K, 2K, 4K |
| Aspect ratios | 1:1, 3:2, 2:3, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9, **1:4, 4:1, 1:8, 8:1** | 1:1, 3:2, 2:3, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9 |
| Reference images | Up to 14 per prompt | Up to 14 per prompt |
| Web/image search | Yes (real-time) | Yes |
| Thinking mode | Yes (toggle ON/OFF) | Yes |
| Watermark | C2PA + SynthID | C2PA + SynthID |
| Knowledge cutoff | January 2025 | January 2025 |

**Thumbnail aspect ratio:** Always use 16:9.

---

## Cost Optimization

**512px Batch-to-Upscale Workflow** (recommended for thumbnail ideation):
1. Generate many 512px variations via Batch API (50% discount)
2. Review and pick the best composition
3. Ask NB2 to upscale the winner to 1K, 2K, or 4K

512px generation costs roughly the same as Nano Banana 1.

---

## Thinking Mode

- **Default: OFF** — faster, sufficient for standard thumbnail prompts
- **Turn ON only for:**
  - Nonsensical/broken results that need reasoning
  - Complex infographics
  - Image grounding combined with spatial reasoning

---

## Core Prompting Principles

1. **Be specific** — concrete details on subject, lighting, composition
2. **Positive framing** — describe what you want, not what you don't ("empty street" not "no cars")
3. **Control the camera** — use photographic/cinematic terms ("low angle", "aerial view", "shallow depth of field")
4. **Iterate conversationally** — refine with follow-up prompts rather than rewriting from scratch
5. **Start with a strong verb** — tells the model the primary operation (Generate / Edit / Transform / Create)

---

## Prompt Formula: Text-to-Image (No References)

```
[Subject] + [Action] + [Location/Context] + [Composition] + [Style]
```

**Example:**
> A striking fashion model wearing a tailored brown dress, sleek boots, and holding a structured handbag. Posing with a confident, statuesque stance, slightly turned. A seamless, deep cherry red studio backdrop. Medium-full shot, center-framed. Fashion magazine style editorial, shot on medium-format analog film, pronounced grain, high saturation, cinematic lighting effect.

---

## Prompt Formula: Multimodal (With Reference Images)

```
[Reference images] + [Relationship instruction] + [New scenario]
```

Up to 14 reference images per prompt. Use for character consistency or placing products in new environments.

---

## Creative Director Prompting Controls

### Lighting
Describe the exact lighting setup — don't leave it to chance.

| Goal | Prompt |
|---|---|
| Even product lighting | "three-point softbox setup" |
| Dramatic / moody | "Chiaroscuro lighting with harsh, high contrast" |
| Warm / natural | "Golden hour backlighting creating long shadows" |
| Tech / authority | "key light upper-left, soft diffused fill from right, rim light creating edge separation from dark background" |

### Camera & Lens
Use specific hardware terminology to control visual DNA.

| Camera | Effect |
|---|---|
| Sony A7 IV, 85mm f/1.8 | Photorealistic portrait — use for person in thumbnail |
| GoPro | Immersive, distorted, action feel |
| Fujifilm | Authentic film color science |
| Disposable camera | Raw, nostalgic flash aesthetic |

| Lens | Effect |
|---|---|
| f/1.8, shallow depth of field | Subject separation from background |
| Wide-angle | Vast scale, spatial context |
| Macro | Intricate product detail |
| 85mm | Flattering portrait compression |

### Color Grading & Film Stock

| Mood | Prompt |
|---|---|
| Nostalgic / gritty | "as if on 1980s color film, slightly grainy" |
| Modern / moody | "Cinematic color grading with muted teal tones" |
| Dark tech / SaaS | "dark purple/navy background, high contrast, green accent metrics" |
| Cinematic subject separation | "background desaturated to near black-and-white, subject remains full color, strong tonal separation" |

### Materiality & Texture
Don't say "jacket" — say "navy blue tweed jacket". Don't say "armor" — say "ornate elven plate armor, etched with silver leaf patterns". Specificity prevents generic AI output.

---

## Portrait Anchor (Use for Every Person in Thumbnail)

Always include this block when a person is in the shot:

```
Shot on Sony A7 IV, 85mm f/1.8, shallow depth of field, slight natural grain,
photorealistic portrait, natural skin pores visible, individual hair strands,
slight flyaways, single catchlight in each eye, candid documentary energy,
natural asymmetric expression, editorial magazine quality
```

---

## Spatial Precision (NB2 Responds Well to This)

Use frame-percentage language for precise layout control:

- "occupies left 40% of frame"
- "upper-right 15% from edge"
- "lower-third of the image"
- "center 60%, leaving 20% margin on each side"

---

## Text Rendering

NB2 handles in-image text well. Rules for best results:

- Enclose text in quotes: `"STOP DOING THIS"`
- Name the font: `"bold white sans-serif"` or `"Century Gothic 12px"`
- Generate text concepts conversationally first, then ask for the image
- For multiple text styles, describe each line separately with its font and weight
- For critical text (small size, precise placement): **composite in Canva/Figma post-generation**

---

## Image Grounding (Visual Search)

NB2 can search the web for real images before generating. Use for:

- Specific real locations (churches, bridges, city squares)
- Exact animal species or breeds
- Niche buildings or monuments

**Cannot** search for people.

**Example prompt formula:**
> "Generate a [style] image of [specific real location/subject]. Ensure [specific architectural/visual details] are accurate to reality."

---

## Editing Mode

When editing an existing image (not generating from scratch):

- Focus on what's changing AND what must stay the same
- Semantic masking: define the region to edit through text — "remove only the man in the background, keep everything else identical"
- Style transfer: "recreate this exact scene in a Van Gogh painting style"
- Composition: upload base image + object image, instruct on how to merge

---

## What to Generate vs. Composite in Post

| Generate directly | Composite in Canva/Figma |
|---|---|
| Large background depth text | Two-tier color bars (need font precision) |
| Broad paint stroke banners | Brand pill badges |
| Large single-word provocations | Any text under 50px equivalent |
| Subject lighting and expression | Precise metric overlays |
| Background and environment | Logos at small sizes |

**Always tell the user:** Generate the base image first. Then bring into Canva or Figma for text overlays — you'll get real font control and pixel-perfect results.

---

## Negative Prompt Template

```
CGI, 3D render, digital art, illustration, anime, cartoon, painting,
perfectly symmetrical face, artificial skin texture, porcelain smooth skin,
skin with no pores, plastic appearance, over-retouched, beauty filter,
stock photo expression, posed smile, generic neutral expression,
glassy artificial eyes, perfectly placed every hair, AI art aesthetic,
corporate headshot lighting, flat featureless lighting, gradient bleeding
subject into background, blurry or unreadable text, cluttered composition,
more than 3 competing focal points, lens flare, watermark, distorted hands,
floating elements with no shadow, perfect symmetry with no tension,
advertising campaign quality, product photography style skin,
HDR over-processing, unnatural color grading
```