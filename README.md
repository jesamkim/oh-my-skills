# oh-my-skills

Open collection of Claude Code skills for AWS-focused workflows, visual content generation, and agent automation.

## Available Skills

| Skill | Description |
|-------|-------------|
| [`aws-diagram`](my-skills/aws-diagram/) | Generate professional AWS architecture diagrams (SVG / PPTX) with official AWS Architecture Icons. |
| [`myslide`](my-skills/myslide/) | Build AWS-themed PowerPoint decks (dark reInvent / light L100 themes) with SVG diagrams and brand colors. |
| [`svg-diagram`](my-skills/svg-diagram/) | Pixel-perfect SVG diagram, banner, and hero graphic generator with anti-overlap rules. |
| [`readme`](my-skills/readme/) | Generate polished, professional README.md files following community best practices. |
| [`paper-finder`](my-skills/paper-finder/) | Search academic papers across Semantic Scholar, OpenAlex, and ArXiv with BibTeX export. |
| [`youtube-script`](my-skills/youtube-script/) | Extract captions / subtitles from YouTube videos (Korean, English, etc.). |
| [`agentcore-browser`](my-skills/agentcore-browser/) | AWS Bedrock AgentCore Browser automation via CDP over SigV4-signed WebSocket. |
| [`computer-use`](my-skills/computer-use/) | Anthropic Computer Use pattern for automated GUI interactions. |
| [`kiro`](my-skills/kiro/) | Delegate tasks to Kiro CLI when Claude Code context is insufficient or an isolated session is needed. |

> `my-skills/scripts/` contains shared helper scripts used by the above skills (e.g. AWS icon extraction).

## Installation

This repository is structured as a Claude Code plugin marketplace.

```bash
# Clone into a location Claude Code can read
git clone https://github.com/<your-user>/oh-my-skills.git
```

Then register it with Claude Code as a local plugin source. Each skill under `my-skills/` has its own `SKILL.md` documenting its trigger phrases and usage.

## Structure

```
oh-my-skills/
├── .claude-plugin/
│   └── marketplace.json     # Plugin marketplace descriptor
├── my-skills/
│   ├── aws-diagram/
│   ├── myslide/
│   ├── svg-diagram/
│   ├── readme/
│   ├── paper-finder/
│   ├── youtube-script/
│   ├── agentcore-browser/
│   ├── computer-use/
│   ├── kiro/
│   └── scripts/             # Shared helpers
├── LICENSE
└── README.md
```

## License

MIT. See [LICENSE](LICENSE).
