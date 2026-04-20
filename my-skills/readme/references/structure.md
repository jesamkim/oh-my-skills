# README Structure Patterns

Project type별 README 구조 패턴 가이드.

## Table of Contents

- [Universal Structure](#universal-structure)
- [Open-Source Library](#open-source-library)
- [CLI Tool](#cli-tool)
- [Web Application](#web-application)
- [API / Backend Service](#api--backend-service)
- [Internal / Corporate Project](#internal--corporate-project)
- [Data Science / ML Project](#data-science--ml-project)
- [Monorepo](#monorepo)

---

## Universal Structure

Every README should follow this cognitive flow:

```
HOOK       → Logo + one-line description + badges
SHOW       → Screenshot / GIF / diagram
CONVINCE   → Features / why this exists
START      → Installation + Quick Start
LEARN      → Usage examples + API reference
ORIENT     → Architecture (if complex)
CONTRIBUTE → Contributing guide + Code of Conduct
CLOSE      → License + credits
```

---

## Open-Source Library

Best for: npm packages, pip packages, gems, crates, Go modules

```markdown
<div align="center">
  <img src="logo.png" alt="LibName" width="120"/>
  <h1>LibName</h1>
  <p>One sentence: what it does and for whom.</p>

  [![npm version](badge)](link)
  [![build](badge)](link)
  [![coverage](badge)](link)
  [![license](badge)](link)
</div>

## Features

- Feature A with brief explanation
- Feature B with brief explanation
- Feature C with brief explanation

## Installation

\```bash
npm install libname
\```

## Quick Start

\```typescript
import { thing } from 'libname';

const result = thing.doSomething({ option: true });
console.log(result);
\```

## Usage

### Basic Usage
(simple example)

### Advanced Usage
(complex example with options)

### With Framework X
(integration example)

## API Reference

### `function(param: Type): ReturnType`
Description of what it does.

| Parameter | Type     | Default | Description       |
|-----------|----------|---------|-------------------|
| param     | `string` | -       | What this param does |

## Benchmarks

(optional: performance comparison table or chart)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
```

---

## CLI Tool

Best for: command-line utilities, dev tools, scripts

```markdown
<div align="center">
  <img src="demo.gif" alt="tool-name demo" width="600"/>
  <h1>tool-name</h1>
  <p>What it does in one sentence.</p>

  [![version](badge)](link)
  [![build](badge)](link)
  [![license](badge)](link)
</div>

## Installation

\```bash
# Homebrew
brew install tool-name

# npm
npm install -g tool-name

# Binary
curl -sSL https://install.example.com | sh
\```

## Quick Start

\```bash
# Initialize
tool-name init

# Run the main thing
tool-name run --flag value
\```

## Commands

| Command               | Description                    |
|-----------------------|--------------------------------|
| `tool-name init`      | Initialize a new project       |
| `tool-name run`       | Run the main process           |
| `tool-name config`    | Manage configuration           |

## Configuration

\```yaml
# ~/.tool-name.yml
option_a: value
option_b: true
nested:
  key: value
\```

## Examples

### Example 1: Common Use Case
(walkthrough with commands and expected output)

### Example 2: Advanced Workflow
(more complex scenario)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
```

---

## Web Application

Best for: web apps, dashboards, SaaS tools

```markdown
<div align="center">
  <img src="banner.png" alt="AppName" width="100%"/>
</div>

<div align="center">
  <h1>AppName</h1>
  <p>Brief description of what the app does and who it's for.</p>

  [![Deploy](https://vercel.com/button)](deploy-link)
  [![Demo](https://img.shields.io/badge/demo-live-brightgreen)](demo-link)
  [![license](badge)](link)
</div>

<div align="center">
  <img src="screenshot.png" alt="AppName Screenshot" width="80%"/>
</div>

## Features

- Feature with screenshot/icon
- Feature with screenshot/icon
- Feature with screenshot/icon

## Getting Started

### Prerequisites

- Node.js >= 18
- PostgreSQL 15+

### Installation

\```bash
git clone https://github.com/owner/appname.git
cd appname
cp .env.example .env
npm install
npm run dev
\```

### Environment Variables

| Variable        | Required | Description              |
|----------------|----------|--------------------------|
| `DATABASE_URL` | Yes      | PostgreSQL connection URL |
| `API_KEY`      | Yes      | Third-party API key      |
| `PORT`         | No       | Server port (default: 3000) |

## Architecture

\```mermaid
graph TB
    Client[Browser] --> API[API Server]
    API --> DB[(PostgreSQL)]
    API --> Cache[(Redis)]
    API --> Queue[Task Queue]
\```

## Tech Stack

| Layer     | Technology                |
|-----------|--------------------------|
| Frontend  | React, TypeScript, Tailwind |
| Backend   | Node.js, Express          |
| Database  | PostgreSQL, Prisma         |
| Deploy    | Docker, AWS ECS            |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
```

---

## API / Backend Service

Best for: REST APIs, GraphQL services, microservices

```markdown
# ServiceName API

> Brief description of the API's purpose.

[![Build](badge)](link) [![Version](badge)](link) [![Docs](badge)](link)

## Quick Example

\```bash
curl -X POST https://api.example.com/v1/resource \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
\```

Response:
\```json
{
  "id": "abc123",
  "status": "created",
  "data": { "key": "value" }
}
\```

## Authentication

All requests require a Bearer token in the Authorization header.
See [Authentication Guide](docs/auth.md) for details.

## Endpoints

### Resources

| Method | Endpoint              | Description         |
|--------|-----------------------|---------------------|
| GET    | `/v1/resources`       | List all resources  |
| POST   | `/v1/resources`       | Create a resource   |
| GET    | `/v1/resources/:id`   | Get a resource      |
| PUT    | `/v1/resources/:id`   | Update a resource   |
| DELETE | `/v1/resources/:id`   | Delete a resource   |

### Detailed: Create a Resource

**Request:**
\```json
{
  "name": "string (required)",
  "type": "string",
  "metadata": {}
}
\```

**Response (201):**
\```json
{
  "id": "string",
  "name": "string",
  "created_at": "ISO 8601"
}
\```

## Rate Limits

| Plan  | Requests/min | Requests/day |
|-------|-------------|-------------|
| Free  | 60          | 1,000       |
| Pro   | 600         | 50,000      |

## SDKs

- [JavaScript](link) - `npm install @example/sdk`
- [Python](link) - `pip install example-sdk`

## Self-Hosting

(Docker setup, environment variables, deployment guide)

## License

MIT
```

---

## Internal / Corporate Project

Best for: team tools, internal services, company projects

```markdown
# ProjectName

> What this project does and which team owns it.

**Owner:** Team Name | **Slack:** #channel-name | **Docs:** [Confluence](link)

## Status

| Environment | Status | URL |
|------------|--------|-----|
| Production | Active | https://prod.internal.com |
| Staging    | Active | https://staging.internal.com |

## Architecture

\```mermaid
graph LR
    User --> ALB[Load Balancer]
    ALB --> App[Application]
    App --> RDS[(Database)]
    App --> S3[Object Storage]
\```

## Getting Started

### Prerequisites

- Access to VPN / internal network
- AWS credentials configured
- Docker Desktop installed

### Local Development

\```bash
git clone git@github.com:org/project.git
cd project
cp .env.example .env.local
# Edit .env.local with your credentials
docker compose up -d
npm install
npm run dev
\```

## Deployment

Merging to `main` triggers automatic deployment via CI/CD pipeline.

### Manual Deployment

\```bash
npm run deploy:staging
npm run deploy:production  # Requires approval
\```

## Runbooks

- [Incident Response](docs/runbooks/incident.md)
- [Database Migration](docs/runbooks/migration.md)
- [Scaling](docs/runbooks/scaling.md)

## Team

| Role       | Person        | Contact          |
|------------|---------------|------------------|
| Tech Lead  | Name          | @handle          |
| Backend    | Name          | @handle          |
| Frontend   | Name          | @handle          |

## Related Repos

- [service-a](link) - Description
- [service-b](link) - Description
```

---

## Data Science / ML Project

Best for: ML models, data pipelines, research implementations

```markdown
<div align="center">
  <h1>ProjectName</h1>
  <p>Brief description of the model/method and what problem it solves.</p>

  [![Paper](https://img.shields.io/badge/paper-arXiv-red)](link)
  [![Model](https://img.shields.io/badge/model-HuggingFace-yellow)](link)
  [![License](badge)](link)
</div>

<div align="center">
  <img src="results/comparison.png" alt="Results" width="80%"/>
</div>

## Results

| Method     | Accuracy | F1 Score | Inference Time |
|------------|----------|----------|----------------|
| Baseline   | 85.2%    | 0.84     | 120ms          |
| **Ours**   | **92.7%**| **0.91** | **45ms**       |
| SOTA (prev)| 90.1%    | 0.89     | 200ms          |

## Quick Start

\```python
from projectname import Model

model = Model.from_pretrained("model-name")
result = model.predict(input_data)
\```

## Installation

\```bash
pip install projectname

# Or from source
git clone https://github.com/owner/projectname.git
cd projectname
pip install -e ".[dev]"
\```

## Dataset

(Description, download instructions, format)

## Training

\```bash
python train.py --config configs/default.yaml
\```

## Evaluation

\```bash
python evaluate.py --checkpoint best_model.pt --data test
\```

## Model Architecture

\```mermaid
graph LR
    Input --> Encoder --> Latent[Latent Space] --> Decoder --> Output
\```

## Citation

\```bibtex
@article{author2024title,
  title={Paper Title},
  author={Author Name},
  journal={Journal},
  year={2024}
}
\```

## License

Apache 2.0
```

---

## Monorepo

Best for: multi-package repositories, workspace projects

```markdown
<div align="center">
  <img src="logo.svg" alt="Project" width="150"/>
  <h1>ProjectName</h1>
  <p>Monorepo for the ProjectName ecosystem.</p>
</div>

## Packages

| Package | Version | Description |
|---------|---------|-------------|
| [`@scope/core`](packages/core) | [![npm](badge)](link) | Core library |
| [`@scope/cli`](packages/cli) | [![npm](badge)](link) | CLI tool |
| [`@scope/plugin-a`](packages/plugin-a) | [![npm](badge)](link) | Plugin A |

## Getting Started

\```bash
git clone https://github.com/owner/project.git
cd project
pnpm install    # or npm install
pnpm build      # build all packages
\```

## Development

\```bash
# Run tests across all packages
pnpm test

# Work on a specific package
pnpm --filter @scope/core dev

# Add a dependency to a package
pnpm --filter @scope/cli add lodash
\```

## Architecture

\```
projectname/
  packages/
    core/        # Core library
    cli/         # CLI tool
    plugin-a/    # Plugin A
  apps/
    web/         # Web app (uses core)
    docs/        # Documentation site
  configs/       # Shared configs (tsconfig, eslint)
\```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Please file issues in this repo,
not individual packages.

## License

MIT
```
