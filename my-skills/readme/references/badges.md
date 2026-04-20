# Badge Guide

Shields.io 기반 배지 생성 가이드. 배지는 프로젝트의 건강 상태와 신뢰도를 즉시 전달한다.

## Badge Syntax

```markdown
[![Label](https://img.shields.io/badge/LABEL-VALUE-COLOR)](URL)
```

## Essential Badges by Category

### Build & CI

```markdown
<!-- GitHub Actions -->
[![Build](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/WORKFLOW.yml?branch=main&label=build)](https://github.com/OWNER/REPO/actions)

<!-- CircleCI -->
[![CircleCI](https://img.shields.io/circleci/build/github/OWNER/REPO/main)](https://circleci.com/gh/OWNER/REPO)

<!-- Travis CI -->
[![Travis](https://img.shields.io/travis/com/OWNER/REPO/main)](https://travis-ci.com/OWNER/REPO)
```

### Version & Release

```markdown
<!-- npm -->
[![npm](https://img.shields.io/npm/v/PACKAGE)](https://www.npmjs.com/package/PACKAGE)

<!-- PyPI -->
[![PyPI](https://img.shields.io/pypi/v/PACKAGE)](https://pypi.org/project/PACKAGE/)

<!-- crates.io -->
[![Crates.io](https://img.shields.io/crates/v/PACKAGE)](https://crates.io/crates/PACKAGE)

<!-- GitHub Release -->
[![Release](https://img.shields.io/github/v/release/OWNER/REPO)](https://github.com/OWNER/REPO/releases)
```

### License

```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

<!-- Auto-detect from repo -->
[![License](https://img.shields.io/github/license/OWNER/REPO)](LICENSE)
```

### Downloads & Popularity

```markdown
<!-- npm downloads -->
[![npm downloads](https://img.shields.io/npm/dm/PACKAGE)](https://www.npmjs.com/package/PACKAGE)

<!-- GitHub stars -->
[![Stars](https://img.shields.io/github/stars/OWNER/REPO?style=social)](https://github.com/OWNER/REPO)

<!-- Docker pulls -->
[![Docker Pulls](https://img.shields.io/docker/pulls/OWNER/IMAGE)](https://hub.docker.com/r/OWNER/IMAGE)
```

### Code Quality

```markdown
<!-- Coverage (Codecov) -->
[![codecov](https://codecov.io/gh/OWNER/REPO/branch/main/graph/badge.svg)](https://codecov.io/gh/OWNER/REPO)

<!-- Coverage (Coveralls) -->
[![Coverage](https://coveralls.io/repos/github/OWNER/REPO/badge.svg?branch=main)](https://coveralls.io/github/OWNER/REPO)

<!-- Code Climate -->
[![Maintainability](https://api.codeclimate.com/v1/badges/BADGE_ID/maintainability)](https://codeclimate.com/github/OWNER/REPO)
```

### Platform & Language

```markdown
<!-- Node version -->
[![Node](https://img.shields.io/node/v/PACKAGE)](package.json)

<!-- Python version -->
[![Python](https://img.shields.io/pypi/pyversions/PACKAGE)](https://pypi.org/project/PACKAGE/)

<!-- Platform -->
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey)]()

<!-- TypeScript -->
[![TypeScript](https://img.shields.io/badge/TypeScript-Ready-blue?logo=typescript)](tsconfig.json)
```

### Community & Support

```markdown
<!-- Discord -->
[![Discord](https://img.shields.io/discord/SERVER_ID?label=Discord&logo=discord)](https://discord.gg/INVITE)

<!-- Slack -->
[![Slack](https://img.shields.io/badge/Slack-Join-brightgreen?logo=slack)](https://join.slack.com/t/WORKSPACE)

<!-- Twitter -->
[![Twitter](https://img.shields.io/twitter/follow/HANDLE?style=social)](https://twitter.com/HANDLE)
```

### Status & Maintenance

```markdown
<!-- Actively maintained -->
[![Maintenance](https://img.shields.io/badge/Maintained-yes-green.svg)](https://github.com/OWNER/REPO)

<!-- PRs Welcome -->
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

<!-- Last commit -->
[![Last Commit](https://img.shields.io/github/last-commit/OWNER/REPO)](https://github.com/OWNER/REPO/commits)
```

## Custom Badges

For any label-value-color badge:

```markdown
[![Custom](https://img.shields.io/badge/LABEL-VALUE-COLOR?logo=LOGO&logoColor=white)](URL)
```

**Color options:** `brightgreen`, `green`, `yellowgreen`, `yellow`, `orange`, `red`, `blue`, `lightgrey`

**Logo options:** Use any [Simple Icons](https://simpleicons.org/) name:
`python`, `typescript`, `react`, `docker`, `aws`, `rust`, `go`, `vue`, etc.

## Badge Styles

Append `?style=STYLE` to any badge URL:

| Style | Look |
|-------|------|
| `flat` (default) | Standard flat badges |
| `flat-square` | Flat with square corners |
| `plastic` | Glossy 3D look |
| `for-the-badge` | Large, bold badges |
| `social` | GitHub social style |

Example:
```markdown
[![npm](https://img.shields.io/npm/v/PACKAGE?style=for-the-badge)](link)
```

## Badge Layout

Center badges under the header for visual balance:

```markdown
<div align="center">

[![badge1](url)](link) [![badge2](url)](link) [![badge3](url)](link)

</div>
```

Separate badge groups with line breaks if there are many:

```markdown
<div align="center">

[![build](url)](link) [![coverage](url)](link) [![version](url)](link)

[![license](url)](link) [![downloads](url)](link) [![stars](url)](link)

</div>
```

## Priority Guide

Not every project needs all badges. Choose based on relevance:

| Priority | When to Include |
|----------|----------------|
| Build status | Always (if CI exists) |
| Version | Published packages |
| License | Open-source projects |
| Coverage | Projects with tests |
| Downloads | Popular packages |
| Platform | Multi-platform tools |
| TypeScript | TS projects |
| PRs Welcome | Seeking contributors |
