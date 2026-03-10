---
name: optimizing-responsive-images
description: Use when building sites with images that need responsive sizing, format conversion, or srcset/sizes implementation. Triggers include portfolio sites, project showcases, image galleries, blog post images, photography sites, or any multi-breakpoint image display.
---

# Optimizing Responsive Images

## Overview

**Core principle:** 3 variants + WebP + correct `sizes` covers 95% of use cases. The primary mistake is over-engineering — too many sizes, too many formats, too many tools.

## The Three-Variant Pipeline

Generate three WebP variants per source image using ImageMagick:

```bash
magick source.jpg -strip -quality 80 -define webp:method=6 project.webp
magick source.jpg -strip -resize 960x -quality 80 -define webp:method=6 project-960.webp
magick source.jpg -strip -resize 480x -quality 80 -define webp:method=6 project-480.webp
```

**Why 3, not 6+:** The 480/960/full spread covers mobile 1x, mobile 2x & desktop 1x, and desktop 2x & lightbox. Going from 3 to 6 saves marginal bytes while tripling complexity.

### Adapting Sizes to Layout

The 480/960/full defaults work for **grid items** (cards, thumbnails, multi-column layouts). For **full-width hero images**, shift the breakpoints up:

```bash
# Full-width hero: 768 / 1440 / 2400
magick source.jpg -strip -resize 2400x -quality 80 -define webp:method=6 hero.webp
magick source.jpg -strip -resize 1440x -quality 80 -define webp:method=6 hero-1440.webp
magick source.jpg -strip -resize 768x -quality 80 -define webp:method=6 hero-768.webp
```

**Cap full-size at ~2400px for web delivery.** Source images from DSLRs (6000px+) are far too large — browsers never need more than ~2400px even on 2x displays at common viewport widths.

## ImageMagick Flags

| Flag | Purpose |
|------|---------|
| `-quality 80` | WebP sweet spot for both screenshots and photos. |
| `-define webp:method=6` | Max compression effort (0-6). Slowest but smallest. Worth it at build time. |
| `-resize 960x` | Width-constrained resize, height scales proportionally. |
| `-strip` | **Removes EXIF/GPS metadata.** Critical for DSLR photos — source files contain GPS coordinates, camera model, lens info. Privacy concern. |
| `-colorspace sRGB` | Add when processing DSLR photos that may use Adobe RGB or ProPhoto RGB. Prevents color shifts on web. Not needed for screenshots/web exports. |

## Format Choice

**Default to WebP only** (97%+ browser support). Add AVIF via `<picture>` only if cutting-edge performance is explicitly required — it triples file count. PNG/JPEG fallbacks are unnecessary for modern sites.

## `srcset` and `sizes`

```html
<img
  src="project.webp"
  srcset="project-480.webp 480w, project-960.webp 960w"
  sizes="(max-width: 30rem) 100vw, (max-width: 50rem) 40vw, 25vw"
  width="1850" height="1040"
  loading="lazy"
  alt="Project screenshot"
/>
```

### How the Browser Picks

The browser selects from `srcset` **before layout**, using `sizes` × DPR:

```
effective pixels needed = sizes value × DPR
```

**1440px desktop, 2x DPR:** `25vw` = 360px → 360 × 2 = 720px → picks `project-960.webp` (smallest ≥ 720)

**375px phone, 2x DPR:** `100vw` = 375px → 375 × 2 = 750px → picks `project-960.webp`

### Writing `sizes`

Match CSS breakpoints. Use `vw`, `px`, or `rem` only. Slightly overestimate rather than risk a too-small image.

## Common Mistakes

### `cqi` Units in `sizes`

**Broken.** `sizes` is evaluated before CSS layout — container query units can't resolve. Browser falls back to a tiny value and always picks the smallest candidate.

```html
<!-- BROKEN -->  sizes="40cqi"
<!-- CORRECT --> sizes="40vw"
```

### Too Many Variants

6 sizes × 3 formats = 18 files per image. Stick to 3 variants unless you have measured data justifying more.

### Missing `width`/`height`

Omitting them causes Cumulative Layout Shift (CLS). Always set intrinsic dimensions.

### Missing `loading="lazy"`

Add to below-the-fold images. For first visible image, omit or use `loading="eager"` with `fetchpriority="high"`.

## Expected File Sizes (WebP, q80)

| Content Type | Full | 960px | 480px |
|-------------|------|-------|-------|
| UI screenshots (~1850px source) | 15-50 KB | 9-20 KB | 4-7 KB |
| Photography (capped ~2400px) | 200-600 KB | 80-200 KB | 30-80 KB |

Photos are 5-10x larger than screenshots at the same dimensions — photographic detail compresses less than flat UI colors. If photo files are unexpectedly large, this is normal.
