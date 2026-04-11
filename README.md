# Just Another Skill

A Claude Code plugin marketplace hosting 9 individual plugins for AI image generation, video production, writing automation, and creative direction.

## What is this?

This is a **Claude Code plugin marketplace** - a repository that hosts multiple plugins as a unified catalog. Users can:
- Add the entire marketplace once with `/plugin marketplace add`
- Install individual plugins they need with `/plugin install`
- Each plugin can be installed independently without others

## Available Plugins

| Plugin | Category | Description |
|--------|----------|-------------|
| **openrouter-images-skill** | Creative | AI image generation via OpenRouter. Text-to-image, image editing, batch processing. |
| **visual-prompt-crafter** | Creative | Craft and improve visual prompts for AI image generators. |
| **ai-director** | Creative | Master framework for AI image generation, video direction, and storytelling. |
| **thumbnail-creator** | Creative | YouTube thumbnail creative director with 33+ techniques. |
| **humanizer** | Writing | Remove AI writing patterns. Makes text sound natural and human-written. |
| **human-voice** | Writing | Transform thoughts into polished communications (emails, pitches, replies). |
| **seedance-director** | Video | Video prompt director for Seedance 2.0. Scene descriptions → production prompts. |
| **n8n-node-builder** | Automation | Build custom n8n community nodes from scratch. |
| **easypanel-template** | Deployment | Generate production-ready Easypanel deployment templates. |

## Installation

### Add the Marketplace (One-time)

```bash
/plugin marketplace add ddm21/just-another-skill
```

### Install Individual Plugins

Install the plugins you need:

```bash
# Single plugin
/plugin install humanizer@just-another-skill

# Multiple plugins
/plugin install openrouter-images-skill@just-another-skill
/plugin install seedance-director@just-another-skill
/plugin install humanizer@just-another-skill
```

### View Available Plugins

```bash
/plugin list
```

## Using Plugins

Once installed, each plugin's skills become available as slash commands:

```bash
/humanizer          # Remove AI writing patterns
/openrouter-images  # AI image generation
/seedance-director  # Video prompt creation
```

## Alternative: Clone & Test Locally

```bash
git clone https://github.com/ddm21/just-another-skill.git
claude --plugin-dir ./just-another-skill
```

## For Developers

Each plugin is located in `plugins/<plugin-name>/`:

```
plugins/
├── openrouter-images-skill/
│   ├── .claude-plugin/plugin.json
│   ├── skills/openrouter-images-skill/SKILL.md
│   ├── scripts/
│   ├── references/
│   └── README.md
├── humanizer/
│   ├── .claude-plugin/plugin.json
│   ├── skills/humanizer/SKILL.md
│   └── README.md
└── [7 more plugins...]
```

The marketplace is defined in `.claude-plugin/marketplace.json`.

## License

MIT