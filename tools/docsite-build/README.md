# Documentation Site Build

This directory contains build scripts for generating the Itqahn documentation site using MkDocs.

---

## Overview

The docsite build process:

1. Validates all documentation files
2. Generates navigation from directory structure
3. Builds static HTML site
4. Deploys to hosting platform

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Serve locally
mkdocs serve

# Build static site
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

---

## Configuration

### mkdocs.yml

```yaml
site_name: Itqahn Documentation
site_description: Autonomous Company-as-Software Platform
site_url: https://docs.itqahn.io

theme:
  name: material
  palette:
    primary: blue
    accent: light blue
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - search.highlight
    - content.code.copy

nav:
  - Overview:
    - Introduction: 00-overview/index.md
    - Glossary: 00-overview/glossary.md
    - Principles: 00-overview/principles.md
  - Product:
    - Vision: 01-product/product-vision.md
    - Build Types: 01-product/supported-build-types.md
    - Phase Gates: 01-product/lifecycle-phase-gates.md
    - Requirements: 01-product/requirements-schema.md
    - ADR Policy: 01-product/adr-policy.md
  # ... continue for all sections

plugins:
  - search
  - mermaid2

markdown_extensions:
  - admonition
  - codehilite
  - pymdownx.superfences
  - pymdownx.tabbed
  - toc:
      permalink: true

extra:
  version:
    provider: mike
```

---

## Directory Structure

```
docsite-build/
├── mkdocs.yml           # MkDocs configuration
├── requirements.txt     # Python dependencies
├── build.sh             # Build script
├── validate.py          # Documentation validator
└── nav_generator.py     # Auto-generate navigation
```

---

## Build Script

```bash
#!/bin/bash
# build.sh - Build documentation site

set -e

echo "Validating documentation..."
python tools/docsite-build/validate.py

echo "Generating navigation..."
python tools/docsite-build/nav_generator.py

echo "Building site..."
mkdocs build --strict

echo "Build complete: site/"
```

---

## Validation

The validator checks:

| Check | Description |
|-------|-------------|
| Broken links | Internal links resolve |
| Missing files | Referenced files exist |
| Frontmatter | Required metadata present |
| Code blocks | Language specified |
| Images | Alt text present |

```bash
# Run validation only
python tools/docsite-build/validate.py

# Validate specific directory
python tools/docsite-build/validate.py --path docs/04-security/
```

---

## CI Integration

```yaml
# .github/workflows/docs.yaml
name: Documentation

on:
  push:
    paths:
      - 'docs/**'
      - 'mkdocs.yml'
  pull_request:
    paths:
      - 'docs/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r tools/docsite-build/requirements.txt

      - name: Validate docs
        run: python tools/docsite-build/validate.py

      - name: Build site
        run: mkdocs build --strict

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to GitHub Pages
        run: mkdocs gh-deploy --force
```

---

## Related

- `docs/` — Documentation source
- `README.md` — Project overview

---

**Version**: 2.0.0 | **Date**: 2026-01-06
