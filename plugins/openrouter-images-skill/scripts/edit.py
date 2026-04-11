#!/usr/bin/env python3
"""OpenRouter Images -- Image Editing

Edit images via OpenRouter API using openai-python.
Uses Gemini 3.1 (Nano Banana 2) - best for editing.

Usage:
    edit.py --image path/to/image.png --prompt "remove the background"
            [--resolution 1K]
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
OUTPUT_DIR = Path.home() / "Documents" / "nanobanana_generated"

MIME_TO_EXT = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/webp": ".webp",
}


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


def edit_image(image_path, prompt, model, api_key, resolution="1K"):
    """Call OpenRouter API to edit an image using Gemini."""
    image_path = Path(image_path).resolve()
    if not image_path.exists():
        print(json.dumps({"error": True, "message": f"Image not found: {image_path}"}))
        sys.exit(1)

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    messages = [{"role": "user", "content": build_message_content(prompt, [str(image_path)])}]

    extra_body = {
        "modalities": ["image", "text"],
        "image_config": {"image_size": resolution},
    }

    try:
        response = client.chat.completions.create(model=model, messages=messages, extra_body=extra_body)
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
    filename = f"banana_edit_{timestamp}.png"

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

    return {"path": str(saved_paths[0]), "model": model, "source": str(image_path)}


def main():
    parser = argparse.ArgumentParser(description="Edit images via OpenRouter API (uses Nano Banana 2)")
    parser.add_argument("--image", required=True, help="Path to input image")
    parser.add_argument("--prompt", required=True, help="Edit instruction")
    parser.add_argument("--resolution", default=DEFAULT_RESOLUTION, help=f"Resolution: 1K, 2K, 4K (default: {DEFAULT_RESOLUTION})")
    parser.add_argument("--api-key", default=None, help="OpenRouter API key (or set OPENROUTER_API_KEY env)")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print(json.dumps({"error": True, "message": "No API key. Set OPENROUTER_API_KEY env or pass --api-key"}))
        sys.exit(1)

    result = edit_image(image_path=args.image, prompt=args.prompt, model=DEFAULT_MODEL, api_key=api_key, resolution=args.resolution)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
