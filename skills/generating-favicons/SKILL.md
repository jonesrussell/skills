---
name: generating-favicons
description: Use when a project needs favicon files created. Triggers include "favicon", "site icon", "browser tab icon", "apple-touch-icon". Covers SVG favicon design and ICO generation.
---

# Generating Favicons

## Overview

Create favicons using inline SVG for modern browsers and convert to ICO for legacy support. SVG favicons support dark mode via `prefers-color-scheme`.

## Quick Reference

| File | Purpose | Size |
|------|---------|------|
| `icon.svg` | Modern browsers (scalable) | Any viewBox |
| `favicon.ico` | Legacy browsers | 32x32 or 16x16+32x32 |
| `apple-touch-icon.png` | iOS home screen | 180x180 |

## HTML Tags

```html
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/img/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
```

## SVG Design Pattern

Design at a small viewBox (32x32 or 64x64). Keep shapes simple — favicons are tiny.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <!-- Background -->
  <rect width="64" height="64" rx="12" fill="#0f1117"/>
  <!-- Simple letterform or icon -->
  <text x="32" y="46" text-anchor="middle"
        font-family="system-ui, sans-serif" font-weight="800"
        font-size="40" fill="#f59e0b">W</text>
  <!-- Optional dark mode support -->
  <style>
    @media (prefers-color-scheme: light) {
      rect { fill: #f59e0b; }
      text { fill: #0f1117; }
    }
  </style>
</svg>
```

## ICO Generation

Use Playwright to screenshot the SVG at 32x32, or use ImageMagick:

```bash
# ImageMagick
convert icon.svg -resize 32x32 favicon.ico

# Playwright (if no ImageMagick)
# Render SVG in browser at 32x32 viewport, screenshot as PNG
# Then use sharp or jimp to convert PNG→ICO
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Complex artwork at 16px | Simplify to letterform or geometric shape |
| Custom fonts in SVG | Use system fonts — custom fonts won't load |
| Missing `xmlns` attribute | Required for standalone SVG files |
| Forgetting `sizes="any"` on ico link | Tells browser ico is fallback, prefer SVG |
