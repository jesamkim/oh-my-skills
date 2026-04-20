---
name: readme
description: |
  Create beautiful, professional README.md files for any project type.
  Generates visually compelling READMEs with logos, badges, screenshots, GIFs,
  architecture diagrams, clear structure, and polished formatting.
  Covers open-source projects, internal tools, libraries, CLI tools, and APIs.
  Based on 100+ curated best practices from the awesome-readme community.
  Trigger: "readme", "create readme", "make readme", "improve readme",
  "README 만들어", "README 작성", "리드미", "프로젝트 문서화"
license: MIT License
metadata:
  skill-author: Jesam Kim
  version: 1.0.0
allowed-tools: [Read, Write, Edit, Bash, Grep, Glob, Agent, WebFetch]
---

# README Craft - Professional README Generator

Create READMEs that make people stop scrolling and start reading.
A great README is the front door to your project. It should communicate
what the project does, why it matters, and how to get started -- all within
30 seconds of landing on the page.

## Quick Start

1. Read [references/structure.md](references/structure.md) for README structure patterns
2. Read [references/badges.md](references/badges.md) for badge creation
3. Read [references/visual-elements.md](references/visual-elements.md) for visual asset guidance

## Core Philosophy

Tom Preston-Werner said it best: "Write the README first."
A README is not an afterthought -- it is the single most important document
in your repository. It frames the project for every person who encounters it:
users, contributors, hiring managers, and your future self.

The goal is not decoration. The goal is **clarity at a glance**.
Every element you add (logo, badge, GIF, diagram) should reduce the time
it takes someone to understand what this project does and whether they need it.

## Workflow

### Step 1: Understand the Project

Before writing anything, gather context:

- What does this project do? (one sentence)
- Who is the target audience? (developers, data scientists, end users, internal team)
- What is the project type? (library, CLI tool, web app, API, framework, infrastructure)
- What language/framework does it use?
- Is it open-source or internal?
- Does it have a logo or visual identity?

If you have access to the codebase, scan the project structure, package.json
(or equivalent), and any existing documentation to extract this information.

### Step 2: Choose the Right Structure

Select a structure pattern from [references/structure.md](references/structure.md)
based on project type. The core sections every README needs:

1. **Header** -- Logo/banner + project name + one-line description
2. **Badges** -- Build status, version, license, coverage (see [references/badges.md](references/badges.md))
3. **Visual Demo** -- Screenshot, GIF, or diagram showing the project in action
4. **What & Why** -- What problem does it solve? Why should someone care?
5. **Quick Start** -- Fastest path from zero to working (under 5 commands)
6. **Usage** -- Code examples for the most common use cases
7. **API / Configuration** -- Reference documentation (if applicable)
8. **Architecture** -- High-level diagram for complex projects
9. **Contributing** -- How to help (link to CONTRIBUTING.md for details)
10. **License** -- Clear license statement

### Step 3: Craft the Header

The header is the most important visual element. It sets the tone.

**Logo placement:**
```markdown
<div align="center">
  <img src="assets/logo.png" alt="Project Name" width="200"/>
  <h1>Project Name</h1>
  <p><strong>One compelling sentence that explains what this does.</strong></p>
</div>
```

**Banner style** (for projects with strong visual identity):
```markdown
<div align="center">
  <img src="assets/banner.png" alt="Project Name Banner" width="100%"/>
</div>
```

The one-line description is critical. It should answer: "What is this?"
without requiring any prior context. Write it like a dictionary definition,
not a marketing tagline.

Good: "A fast, lightweight key-value store written in Go"
Bad: "The next-generation solution for your data needs"

### Step 4: Add Badges

Badges provide instant credibility and project health signals.
Use [references/badges.md](references/badges.md) for the complete guide.

Place badges right after the header, centered:
```markdown
<div align="center">

[![Build Status](https://img.shields.io/github/actions/workflow/status/owner/repo/ci.yml?branch=main)](link)
[![Version](https://img.shields.io/npm/v/package-name)](link)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](link)
[![Downloads](https://img.shields.io/npm/dm/package-name)](link)

</div>
```

**Badge priority order** (include what's relevant, skip what's not):
1. Build/CI status -- proves the project works
2. Version/Release -- shows active maintenance
3. License -- answers legal questions immediately
4. Test coverage -- signals code quality
5. Downloads/Stars -- social proof
6. Language/Framework -- quick tech identification

### Step 5: Visual Demo

A picture is worth a thousand words. A GIF is worth ten thousand.

**For CLI tools:** Use terminal recording GIFs (vhs, terminalizer, or asciinema)
**For web apps:** Screenshot of the main interface, or a short GIF of the key workflow
**For libraries:** Code snippet + output screenshot side by side
**For APIs:** Show a request/response example with syntax highlighting

```markdown
<div align="center">
  <img src="assets/demo.gif" alt="Demo" width="600"/>
</div>
```

See [references/visual-elements.md](references/visual-elements.md) for tools
and techniques for creating compelling visual assets.

### Step 6: Write the Content

**Installation section:**
- Show the simplest install path first
- Use tabbed code blocks if multiple package managers are supported
- Include prerequisites if any

```markdown
## Installation

```bash
npm install my-package
```

Or with yarn:
```bash
yarn add my-package
```
```

**Usage section:**
- Start with the simplest possible example
- Progress to more complex use cases
- Every code block should be copy-pasteable and runnable

**Architecture section** (for complex projects):
- Use Mermaid diagrams when possible (GitHub renders them natively)
- Keep diagrams high-level; link to detailed docs for depth
- Show data flow, not just component boxes

### Step 7: Table of Contents

For READMEs longer than 3 screen-heights, add a TOC after the badges:

```markdown
## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Configuration](#configuration)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [License](#license)
```

For shorter READMEs, skip the TOC. It adds noise without value.

### Step 8: Polish

- Use consistent heading levels (H2 for main sections, H3 for subsections)
- Add horizontal rules (`---`) sparingly to separate major sections
- Use `<details>` tags for optional/advanced content that would clutter the main flow
- End with a clear license statement and optionally a "Made with" or credits section
- Check all links work
- Verify images render at reasonable sizes

## Project Type Adaptations

**Open-source library:**
Emphasize installation, API docs, code examples, and contributing guide.
Badge priority: version, build, coverage, license, downloads.

**CLI tool:**
Lead with a GIF demo. Focus on install, basic commands, and configuration.
Badge priority: version, build, license, platform support.

**Web application:**
Lead with a screenshot. Include deploy buttons (Vercel, Heroku, etc.)
if applicable. Focus on features, setup, and environment variables.

**Internal/corporate project:**
Skip badges. Focus on setup, architecture, team conventions, and
deployment procedures. Include links to related internal docs.

**API:**
Lead with a request/response example. Include authentication setup,
endpoint reference, and rate limits. Consider linking to interactive
API docs (Swagger/OpenAPI).

## Output Quality Checklist

Before delivering the README, verify:

- [ ] One-line description answers "what is this?" without jargon
- [ ] Someone can go from zero to running in under 2 minutes with the Quick Start
- [ ] All code blocks are syntax-highlighted and copy-pasteable
- [ ] Visual assets (screenshots, GIFs) are present and render correctly
- [ ] Badges are relevant (not decorative padding)
- [ ] No broken links
- [ ] License is clearly stated
- [ ] Consistent formatting throughout
- [ ] No walls of text -- information is scannable
- [ ] README works well in both light and dark GitHub themes
