# Post-Processing Reference

> Load this on-demand when user needs image post-processing.

## ImageMagick Commands

First, verify ImageMagick is available:
```bash
which magick || which convert || echo "ImageMagick not installed"
```

### Remove Background (White → Transparent)

```bash
magick input.png -fuzz 10% -transparent white output.png
```

### Remove Background (Green Screen)

```bash
magick input.png -fuzz 15% -transparent lime output.png
```

### Crop to Exact Dimensions

```bash
magick input.png -resize 1200x630^ -gravity center -extent 1200x630 output.png
```

### Convert Format

```bash
magick input.png output.webp
magick input.jpg output.png
```

### Add Border/Padding

```bash
magick input.png -bordercolor white -border 20 output.png
```

### Resize for Specific Platform

```bash
# Instagram
magick input.png -resize 1080x1080 instagram.png

# Twitter
magick input.png -resize 1200x675 twitter.png

# Facebook Cover
magick input.png -resize 820x312 facebook_cover.png
```

### Brightness/Contrast Adjustment

```bash
# Brighten
magick input.png -brightness-contrast 20x0 output.png

# Increase contrast
magick input.png -brightness-contrast 0x20 output.png
```

### Rotate Image

```bash
magick input.png -rotate 90 output.png
```

## FFmpeg (Video/GIF)

### Convert to GIF

```bash
ffmpeg -i input.mp4 -vf "fps=10,scale=320:-1:flags=lanczos" output.gif
```

### Extract Frame from Video

```bash
ffmpeg -i video.mp4 -ss 00:00:05 -vframes 1 frame.jpg
```

## Notes

- Use `magick` (ImageMagick 7) if available, otherwise `convert` (v6)
- Always verify tools are installed before promising post-processing
- For batch operations, use loops or scripts
