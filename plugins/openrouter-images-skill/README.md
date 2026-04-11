# OpenRouter Images Skill

AI image generation Creative Director powered by Gemini via OpenRouter. Generate, edit, and create images using any OpenRouter-supported image model.

## What This Skill Does

- **Text-to-Image**: Generate images from prompts
- **Image Editing**: Edit existing images (background removal, style changes, etc.)
- **Batch Generation**: Generate multiple images from CSV
- **Cost Tracking**: Track and estimate generation costs
- **Creative Direction**: Optimizes prompts for best results

## Quick Start

### 1. Set API Key

```bash
# Windows (PowerShell)
$env:OPENROUTER_API_KEY = "sk-or-v1-..."

# Linux/Mac
export OPENROUTER_API_KEY="sk-or-v1-..."
```

Get a free key at: https://openrouter.ai/settings/keys

### 2. Install Dependencies

```bash
pip install openai
```

### 3. Generate an Image

```bash
python scripts/generate.py --prompt "a cozy coffee shop with warm lighting"
```

## Supported Models

| Model ID | Name | Best For | Resolution | Cost/Image |
|----------|------|----------|------------|------------|
| `google/gemini-3.1-flash-image-preview` | **Nano Banana 2** (default) | Best balance | 1K/2K/4K | $0.04-$0.16 |
| `google/gemini-2.5-flash-image` | Nano Banana | Fast, budget | 1K/2K/4K | $0.03-$0.12 |
| `bytedance-seed/seedream-4.5` | Seedream | Editing | 1K/2K | $0.04 |
| `sourceful/riverflow-v2-fast` | Riverflow Fast | Text rendering | 1K/2K | $0.02-$0.04 |
| `sourceful/riverflow-v2-pro` | Riverflow Pro | Best text | 1K/2K/4K | $0.15-$0.33 |
| `openai/gpt-5-image-mini` | GPT-5 Image Mini | Efficient | 1K/2K | ~$0.02 |

## Commands

### Generate Image

```bash
python scripts/generate.py --prompt "your prompt" [options]

Options:
  --prompt TEXT          Required
  --aspect-ratio TEXT   1:1, 16:9, 9:16, 4:3, etc. (default: 1:1)
  --resolution TEXT     1K, 2K, 4K (default: 1K)
  --model TEXT          Model ID
```

### Edit Image

```bash
python scripts/edit.py --image path/to/image.png --prompt "edit instructions"
```

### Batch Generation

```bash
python scripts/batch.py --csv path/to/file.csv
```

### Cost Tracking

```bash
python scripts/cost_tracker.py log --model "..." --resolution 1K --prompt "..."
python scripts/cost_tracker.py summary
python scripts/cost_tracker.py today
python scripts/cost_tracker.py estimate --model "..." --resolution 1K --count 10
```

## Output

Images are saved to: `~/Documents/nanobanana_generated/`

## Installation

### Plugin Install (Recommended)

```bash
/plugin marketplace add ddm21/openrouter-images-skill
/plugin install openrouter-images-skill@openrouter-images-skill-marketplace
```

Or test locally:

```bash
git clone https://github.com/ddm21/openrouter-images-skill.git
claude --plugin-dir ./openrouter-images-skill
```
