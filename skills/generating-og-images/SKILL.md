---
name: generating-og-images
description: Use when a project needs Open Graph social card images generated from HTML templates via Playwright screenshot. Triggers include "OG image", "social card", "social preview image", "og:image", "twitter:image".
---

# Generating OG Images

## Overview

Generate branded 1200x630 OG images by rendering an HTML template with Playwright and screenshotting it. No image editor needed — design in HTML/CSS, capture as PNG.

## Core Pattern

1. **HTML template** — Self-contained 1200x630 page with CSS, placeholder variables (`{{title}}`, `{{gradient}}`, etc.)
2. **Node.js script** — Reads content source, injects variables, screenshots via Playwright
3. **Incremental mode** — SHA-256 hash of template detects changes; only regenerates when needed

## Quick Reference

| Component | Convention |
|-----------|-----------|
| Viewport | 1200x630px (OG standard) |
| Template | `scripts/og-template.html` |
| Script | `scripts/generate-og-images.js` |
| Output | `public/img/og/` or `static/images/og/` |
| Hash file | `.og-template-hash` in output dir |
| Font | System stack (no external fonts = no load delay) |

## Template Design Rules

- Fixed 1200x630 body, `overflow: hidden`
- Use `linear-gradient(135deg, ...)` backgrounds for visual interest
- Decorative elements (circles, borders) at low opacity (`rgba(255,255,255,0.08-0.12)`)
- Title font size adapts to length: `<40 chars → 64px`, `40-80 → 48px`, `>80 → 36px`
- White text on gradient, author/subtitle at 70% opacity
- Badge/label for category/series with `rgba(255,255,255,0.2)` background

## Script Structure

```javascript
const { chromium } = require('playwright');
const fs = require('fs');
const crypto = require('crypto');

// 1. Read template, compute hash
// 2. Compare hash to detect template changes
// 3. Find content items needing images
// 4. For each: inject variables → setContent → screenshot
// 5. Save hash file

const browser = await chromium.launch();
const page = await browser.newPage();
await page.setViewportSize({ width: 1200, height: 630 });

// Variable injection via string replacement
const html = template
  .replace(/\{\{title\}\}/g, escapedTitle)
  .replace(/\{\{gradient\}\}/g, gradient);

await page.setContent(html, { waitUntil: 'load' });
await page.screenshot({ path: outputPath, type: 'png' });
```

## For Single-Page Sites (no content scanning)

Skip the incremental/scanning logic. Just render one template:

```javascript
const { chromium } = require('playwright');
const fs = require('fs');

const template = fs.readFileSync('scripts/og-template.html', 'utf-8');
const browser = await chromium.launch();
const page = await browser.newPage();
await page.setViewportSize({ width: 1200, height: 630 });
await page.setContent(template, { waitUntil: 'load' });
await page.screenshot({ path: 'public/img/og-card.png', type: 'png' });
await browser.close();
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| External fonts cause blank text | Use system font stack |
| Title overflows card | Adaptive font sizing by character count |
| Unescaped HTML in title | Escape `&` → `&amp;`, `<` → `&lt;` |
| Regenerating unchanged images | Hash template, skip if unchanged |
| Missing `waitUntil: 'load'` | Playwright may screenshot before CSS applies |
