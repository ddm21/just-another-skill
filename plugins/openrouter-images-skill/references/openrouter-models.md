# OpenRouter Image Models Reference

This document details supported image generation models on OpenRouter and their parameters.

## Model Categories

### Google Gemini Models

| Model ID | Name | Best For | Resolutions | Aspect Ratios |
|----------|------|----------|-------------|---------------|
| `google/gemini-3.1-flash-image-preview` | Nano Banana 2 | **Default** - Best balance | 0.5K, 1K, 2K, 4K | All (including extended) |
| `google/gemini-2.5-flash-image` | Nano Banana | Fast, budget | 1K, 2K, 4K | Standard only |

**Gemini Parameters:**
```json
{
  "modalities": ["image", "text"],
  "image_config": {
    "aspect_ratio": "16:9",
    "image_size": "2K"
  }
}
```

**Extended Aspect Ratios** (Gemini 3.1 only):
- `1:4` - Extra tall, narrow (carousels, vertical UI)
- `4:1` - Extra wide, short (hero banners)
- `1:8` - Extra tall for notification headers
- `8:1` - Extra wide for panoramic layouts

### Sourceful Models

| Model ID | Name | Best For | Resolutions | Special Features |
|----------|------|----------|-------------|-------------------|
| `sourceful/riverflow-v2-pro` | Riverflow Pro | Best text rendering | 1K, 2K, 4K | font_inputs |
| `sourceful/riverflow-v2-fast` | Riverflow Fast | Fast production | 1K, 2K | font_inputs |

**Sourceful Parameters:**
```json
{
  "modalities": ["image"],
  "image_config": {
    "aspect_ratio": "16:9",
    "image_size": "2K"
  }
}
```

**Note:** Sourceful models work best with image URLs instead of Base64. 4.5MB request limit.

### ByteDance Seedream

| Model ID | Name | Best For | Resolutions |
|----------|------|----------|-------------|
| `bytedance-seed/seedream-4.5` | Seedream 4.5 | Editing, consistency | 1K, 2K |

### OpenAI GPT-5 Image

| Model ID | Name | Best For | Resolutions |
|----------|------|----------|-------------|
| `openai/gpt-5-image-mini` | GPT-5 Image Mini | Efficient | 1K, 2K |

## Universal Parameters

| Parameter | Description | Values |
|-----------|-------------|--------|
| `modalities` | Output types | `["image"]` or `["image", "text"]` |
| `image_config.aspect_ratio` | Image shape | `1:1`, `16:9`, `9:16`, `4:3`, etc. |
| `image_config.image_size` | Resolution | `0.5K`, `1K`, `2K`, `4K` |

## Model-Specific Handling

- **Gemini models**: Use `modalities: ["image", "text"]` + `image_config`
- **Sourceful/Seedream/GPT-5**: Use `modalities: ["image"]` + `image_config`

## Resolution Mapping

| Size | Dimensions (approx) |
|------|---------------------|
| `0.5K` | 512×512 (Gemini 3.1 only) |
| `1K` | 1024×1024 (Default) |
| `2K` | 2048×2048 |
| `4K` | 4096×4096 |

## Aspect Ratio Mapping

| Ratio | Dimensions |
|-------|------------|
| `1:1` | 1024×1024 |
| `16:9` | 1344×768 |
| `9:16` | 768×1344 |
| `4:3` | 1184×864 |
| `21:9` | 1536×672 |
