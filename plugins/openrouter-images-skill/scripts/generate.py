#!/usr/bin/env python3
"""OpenRouter Images -- Image Generation

Generate images via OpenRouter API using openai-python.

Supported models:
    google/gemini-3.1-flash-image-preview  - Nano Banana 2 (default)
    google/gemini-3-pro-image-preview       - Nano Banana Pro
    google/gemini-2.5-flash-image           - Nano Banana
    bytedance-seed/seedream-4.5              - Seedream
    sourceful/riverflow-v2-fast              - Riverflow
    sourceful/riverflow-v2-pro               - Riverflow Pro
    openai/gpt-5-image-mini                  - GPT-5 Image Mini

Usage:
    generate.py --prompt "a cat in space" [--aspect-ratio 16:9] [--resolution 1K]
                [--model MODEL] [--filename NAME]
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
from datetime import datetime
from pathlib import Path

from openai import OpenAI

DEFAULT_MODEL = "google/gemini-3.1-flash-image-preview"
DEFAULT_RESOLUTION = "1K"
DEFAULT_RATIO = "1:1"
OUTPUT_DIR = Path.home() / "Documents" / "nanobanana_generated"

VALID_RATIOS = {"1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2",
                "4:5", "5:4", "1:4", "4:1", "1:8", "8:1", "21:9"}
VALID_RESOLUTIONS = {"0.5K", "1K", "2K", "4K"}

MIME_TO_EXT = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/webp": ".webp",
}

GEMINI_MODELS = {"google/gemini-3.1-flash-image-preview", "google/gemini-3-pro-image-preview",
                 "google/gemini-2.5-flash-image", "google/gemini-2.5-flash-preview-09-2025"}
SOURCEFUL_MODELS = {"sourceful/riverflow-v2-fast", "sourceful/riverflow-v2-pro",
                    "sourceful/riverflow-v2-max-preview", "sourceful/riverflow-v2-standard-preview",
                    "sourceful/riverflow-v2-fast-preview"}
BYTEDANCE_MODELS = {"bytedance-seed/seedream-4.5"}
OPENAI_MODELS = {"openai/gpt-5-image", "openai/gpt-5-image-mini"}
BLACK_FOREST_MODELS = {"black-forest-labs/flux.2-klein-4b", "black-forest-labs/flux.2-pro",
                       "black-forest-labs/flux.2-flex"}


def get_model_type(model: str) -> str:
    """Determine model type for parameter selection."""
    if any(model.startswith(prefix) for prefix in ["google/gemini"]):
        return "gemini"
    if "sourceful/riverflow" in model:
        return "sourceful"
    if "bytedance-seed" in model:
        return "bytedance"
    if model.startswith("openai/gpt"):
        return "openai"
    if "black-forest-labs" in model:
        return "black_forest"
    return "gemini"


def build_api_params(model: str, prompt: str, aspect_ratio: str, resolution: str,
                     input_images: list = None) -> dict:
    """Build API parameters based on model type."""
    model_type = get_model_type(model)
    
    modalities = ["image", "text"]
    if model_type in ("sourceful", "bytedance", "black_forest"):
        modalities = ["image"]
    
    image_config = {}
    
    if model_type != "black_forest":
        if resolution and resolution != "1K":
            image_config["image_size"] = resolution
        if aspect_ratio and aspect_ratio != "1:1" and model_type in ("gemini", "sourceful"):
            image_config["aspect_ratio"] = aspect_ratio
    
    extra_body = {"modalities": modalities}
    if image_config:
        extra_body["image_config"] = image_config
    
    messages = [{
        "role": "user",
        "content": build_message_content(prompt, input_images or []),
    }]
    
    return {"messages": messages, "extra_body": extra_body}


def encode_image_to_data_url(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    if not mime:
        mime = "image/png"
    data = path.read_bytes()
    encoded = base64.b64encode(data).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def build_message_content(prompt: str, input_images: list[str]) -> list[dict]:
    content: list[dict] = [{"type": "text", "text": prompt}]
    for image_path in input_images:
        data_url = encode_image_to_data_url(Path(image_path))
        content.append({"type": "image_url", "image_url": {"url": data_url}})
    return content


def parse_data_url(data_url: str):
    if not data_url.startswith("data:") or ";base64," not in data_url:
        raise SystemExit("Image URL is not a base64 data URL.")
    header, encoded = data_url.split(",", 1)
    mime = header[5:].split(";", 1)[0]
    try:
        raw = base64.b64decode(encoded)
    except Exception as e:
        raise SystemExit(f"Failed to decode base64 image payload: {e}")
    return mime, raw


def resolve_output_path(filename: str, image_index: int, total_count: int, mime: str) -> Path:
    output_path = Path(filename)
    suffix = output_path.suffix

    expected_suffix = MIME_TO_EXT.get(mime, ".png")
    if suffix and suffix.lower() != expected_suffix.lower():
        suffix = expected_suffix
    elif not suffix:
        suffix = expected_suffix

    if total_count <= 1:
        return output_path.with_suffix(suffix)

    return output_path.with_name(f"{output_path.stem}-{image_index + 1}{suffix}")


def extract_image_url(image) -> str | None:
    if isinstance(image, dict):
        return image.get("image_url", {}).get("url") or image.get("url")
    return None


def generate_image(prompt, model, aspect_ratio, resolution, api_key,
                   thinking_level=None, image_only=False, input_images=None):
    """Call OpenRouter API to generate an image."""
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    api_params = build_api_params(model, prompt, aspect_ratio, resolution, input_images)

    try:
        response = client.chat.completions.create(
            model=model,
            **api_params
        )
    except Exception as e:
        print(json.dumps({"error": True, "message": str(e)}))
        sys.exit(1)

    message = response.choices[0].message
    images = getattr(message, "images", None)
    if not images:
        print(json.dumps({"error": True, "message": "No images returned by the API"}))
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"banana_{timestamp}.png"

    saved_paths = []
    for idx, image in enumerate(images):
        image_url = extract_image_url(image)
        if not image_url:
            continue
        mime, raw = parse_data_url(image_url)
        output_path = resolve_output_path(filename, idx, len(images), mime)
        output_path = OUTPUT_DIR / output_path.name
        output_path.write_bytes(raw)
        saved_paths.append(output_path)

    if not saved_paths:
        print(json.dumps({"error": True, "message": "Failed to save images"}))
        sys.exit(1)

    return {
        "path": str(saved_paths[0]),
        "model": model,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate images via OpenRouter API")
    parser.add_argument("--prompt", required=True, help="Image generation prompt")
    parser.add_argument("--aspect-ratio", default=DEFAULT_RATIO, help=f"Aspect ratio (default: {DEFAULT_RATIO})")
    parser.add_argument("--resolution", default=DEFAULT_RESOLUTION, help=f"Resolution: 0.5K, 1K, 2K, 4K (default: {DEFAULT_RESOLUTION})")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model ID (default: {DEFAULT_MODEL})")
    parser.add_argument("--api-key", default=None, help="OpenRouter API key (or set OPENROUTER_API_KEY env)")
    parser.add_argument("--thinking", default=None, choices=["minimal", "low", "medium", "high"], help="Thinking level (Gemini only)")
    parser.add_argument("--image-only", action="store_true", help="Return image only (not used)")
    parser.add_argument("--input-image", action="append", default=[], help="Input image for editing/compositing")

    args = parser.parse_args()

    if args.aspect_ratio not in VALID_RATIOS:
        print(json.dumps({"error": True, "message": f"Invalid aspect ratio '{args.aspect_ratio}'. Valid: {sorted(VALID_RATIOS)}"}))
        sys.exit(1)

    if args.resolution not in VALID_RESOLUTIONS:
        print(json.dumps({"error": True, "message": f"Invalid resolution '{args.resolution}'. Valid: {sorted(VALID_RESOLUTIONS)}"}))
        sys.exit(1)

    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print(json.dumps({"error": True, "message": "No API key. Set OPENROUTER_API_KEY env or pass --api-key"}))
        sys.exit(1)

    result = generate_image(
        prompt=args.prompt,
        model=args.model,
        aspect_ratio=args.aspect_ratio,
        resolution=args.resolution,
        api_key=api_key,
        thinking_level=args.thinking,
        image_only=args.image_only,
        input_images=args.input_image,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
