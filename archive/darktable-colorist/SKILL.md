---
name: darktable-colorist
description: "professional color grading and post-processing for darktable. Use when the user wants to apply LUT presets, adjust exposure, color grade with curves, create cinematic looks, process RAW photos, batch export, or do any photo editing with darktable. Triggers on: color grading, LUT, CUBE file, curves, exposure, cinematic, film look, photo editing, RAW processing, batch export, darktable, color balance, tone curve, post-processing,调色, 色彩, 曲线, LUT, 预设, 后期, 修图."
---

# darktable-colorist

professional color grading and post-processing skill for darktable.

## Prerequisites

- darktable installed (`darktable-cli` in PATH)
- `cli-anything-darktable` CLI harness installed

```bash
# Verify installation
which darktable-cli
cli-anything-darktable --help
```

## Quick Start

```bash
# Apply a cinematic LUT
cli-anything-darktable lut apply photo.jpg cinematic.cube /output

# Adjust exposure + color grading in one pass
cli-anything-darktable adjust chain photo.jpg /output \
  --ev +0.3 --saturation 0.2 --curve-preset contrast+

# Batch process selected images
cli-anything-darktable adjust chain /output --ids 1,2,3 --ev +0.5
```

---

## LUT Library

CUBE files are stored in:
- `/home/smh/homeconfig/skills/darktable-colorist/assets/luts/`
- `~/homeconfig/skills/darktable-colorist/assets/luts/`

Available LUTs:
- `REC709 2383 D65.cube` — REC709 色彩空间电影胶片模拟
- `ACES CCT 2383 D65.cube` — ACES 色彩空间电影胶片模拟
- `CineStill-800-T-V2.0-N125.cube` — CineStill 800T 胶片
- `PictureFX-LeicaM8-BW-125.cube` — 黑白胶片模拟

### LUT Management

```bash
# Scan LUT library
cli-anything-darktable lut scan assets/luts/

# Validate a CUBE file
cli-anything-darktable lut validate assets/luts/cinematic/kodak2383.cube

# Apply LUT with options
cli-anything-darktable lut apply photo.jpg assets/luts/film/portra400.cube /output \
  --colorspace sRGB --interpolation tetrahedral --format jpg
```

### LUT Naming Convention

```
<filmstock>_<variant>_<strength>.cube
```

Examples:
- `kodak_portra_400.cube` - Kodak Portra 400 film stock
- `fuji_velvia_50_vivid.cube` - Fuji Velvia 50 vivid variant
- `cinematic_teal_orange.cube` - Teal & orange cinema look

---

## Professional Color Grading Workflow

### Step 1: Exposure & White Balance

Start with correct exposure. Use the exposure module:

```bash
# Brighten by 0.7 EV
cli-anything-darktable adjust exposure photo.jpg /output --ev +0.7

# Darken with lifted blacks
cli-anything-darktable adjust exposure photo.jpg /output --ev -0.3 --black 0.02
```

### Step 2: Contrast & Tone Curve

Apply S-curve for contrast:

```bash
# Standard contrast boost
cli-anything-darktable adjust curve photo.jpg /output --preset contrast+

# Lift shadows (fade blacks)
cli-anything-darktable adjust curve photo.jpg /output --preset shadows_lift

# Crush highlights (matte look)
cli-anything-darktable adjust curve photo.jpg /output --preset highlights_crush
```

### Step 3: Color Grading

Use color balance for cinematic color separation:

```bash
# Teal shadows + warm highlights (cinematic)
cli-anything-darktable adjust color-balance photo.jpg /output \
  --shadows-hue 200 --shadows-chroma 0.3 \
  --highlights-hue 40 --highlights-chroma 0.2

# Orange & teal (blockbuster look)
cli-anything-darktable adjust color-balance photo.jpg /output \
  --shadows-hue 190 --shadows-chroma 0.4 \
  --highlights-hue 30 --highlights-chroma 0.3 \
  --global-saturation 0.1

# Desaturated shadows + saturated highlights (film look)
cli-anything-darktable adjust color-balance photo.jpg /output \
  --saturation-shadows -0.3 --saturation-highlights 0.2 \
  --contrast 0.15
```

### Step 4: LUT Application

Apply a film emulation LUT as the final step:

```bash
cli-anything-darktable lut apply photo.jpg assets/luts/film/kodak_portra.cube /output
```

### Full Pipeline (Chain)

Combine all steps in one command:

```bash
cli-anything-darktable adjust chain photo.jpg /output \
  --ev +0.3 \
  --saturation 0.15 \
  --curve-preset contrast+
```

---

## Style Presets（风格预设）

### 清新日系 (Fresh Japanese Style)

**流程：先 REC709 LUT 打底 → 再色彩微调**

```bash
# Step 1: 应用 REC709 LUT 打底
cli-anything-darktable lut apply photo.jpg "/home/smh/homeconfig/skills/darktable-colorist/assets/luts/REC709 2383 D65.cube" /output --format jpg

# Step 2: 在 LUT 基础上色彩微调
cli-anything-darktable adjust chain /output/photo.jpg /output2 \
  --ev +0.3 \
  --curve-preset shadows_lift \
  --saturation -0.15 \
  --vibrance 0.1 \
  --contrast 0.05
```

**参数说明：**
- REC709 LUT 提供标准电影色彩基底，统一色调
- `--ev +0.3` 轻微提亮，营造明亮感
- `--curve-preset shadows_lift` 阴影提亮，淡雅柔和
- `--saturation -0.15` 略降饱和，清新不艳
- `--vibrance +0.1` 保留肤色和天空色彩
- `--contrast +0.05` 柔和对比

**微调方向：**
- 更冷色调：后续加 `--shadows-hue 210 --shadows-chroma 0.1`
- 更暖阳光：后续加 `--highlights-hue 45 --highlights-chroma 0.1`
- 更强褪色：`--curve-preset film_fade` 替代 `shadows_lift`

### 黑白 (Black & White)

**流程：PictureFX Leica M8 黑白胶片模拟**

```bash
# 一步完成黑白转换
cli-anything-darktable lut apply photo.jpg "/home/smh/homeconfig/skills/darktable-colorist/assets/luts/PictureFX-LeicaM8-BW-125.cube" /output --format jpg
```

**可选微调：**
```bash
# 黑白 + 高对比
cli-anything-darktable lut apply photo.jpg "/home/smh/homeconfig/skills/darktable-colorist/assets/luts/PictureFX-LeicaM8-BW-125.cube" /output --format jpg
cli-anything-darktable adjust chain /output/photo.jpg /output2 --contrast 0.3 --format jpg

# 黑白 + 淡雅（提亮阴影）
cli-anything-darktable adjust chain /output/photo.jpg /output2 --curve-preset shadows_lift --ev +0.2 --format jpg

# 黑白 + 高光压制（暗调风格）
cli-anything-darktable adjust chain /output/photo.jpg /output2 --curve-preset highlights_crush --format jpg
```

---

## Color Theory Reference

### Color Harmony

| Harmony | Shadows | Highlights | Use Case |
|---------|---------|------------|----------|
| Complementary | 180° opposite | Base hue | High contrast drama |
| Analogous | ±30° | ±30° | Harmonious, natural |
| Triadic | +120° | +240° | Vibrant, playful |
| Split-complementary | 150° | 210° | Balanced contrast |

### Common Color Grades

**Teal & Orange (Blockbuster)**
```bash
--shadows-hue 190 --shadows-chroma 0.4
--highlights-hue 30 --highlights-chroma 0.3
```

**Warm Vintage**
```bash
--shadows-hue 40 --shadows-chroma 0.2
--highlights-hue 50 --highlights-chroma 0.15
--saturation-global -0.2
```

**Cool Cinematic**
```bash
--shadows-hue 220 --shadows-chroma 0.3
--highlights-hue 200 --highlights-chroma 0.1
--contrast 0.2
```

**Bleach Bypass**
```bash
--saturation-global -0.5
--contrast 0.4
--brilliance-global 0.2
```

**Cross Process**
```bash
--curve-preset cross_process
--shadows-hue 120 --shadows-chroma 0.3
--highlights-hue 30 --highlights-chroma 0.2
```

---

## Curve Presets

| Preset | Effect | Best For |
|--------|--------|----------|
| `contrast+` | S-curve boost | General enhancement |
| `contrast-` | Reverse S-curve | Flat/moody look |
| `shadows_lift` | Lift black point | Faded/film look |
| `highlights_crush` | Lower white point | Matte/desaturated |
| `film_fade` | Lift blacks + lower whites | Vintage film |
| `cross_process` | Color-shifted curve | Creative/artistic |

---

## Batch Processing

```bash
# Process by image IDs
cli-anything-darktable adjust chain /output --ids 1,2,3,4,5 \
  --ev +0.3 --saturation 0.2 --curve-preset contrast+

# Process current selection
cli-anything-darktable library select 10 11 12 13
cli-anything-darktable adjust chain /output --ev +0.5

# Export with style
cli-anything-darktable export batch /output --ids 1,2,3 --style "vivid"
```

---

## Output Formats

| Format | Flag | Use Case |
|--------|------|----------|
| JPEG | `--format jpg` | Web, social media |
| PNG | `--format png` | Lossless, transparency |
| TIFF | `--format tiff` | Print, archive |
| WebP | `--format webp` | Web optimization |
| AVIF | `--format avif` | Next-gen web |

```bash
# High-quality TIFF for print
cli-anything-darktable lut apply photo.jpg film.cube /output --format tiff

# Resized for web
cli-anything-darktable adjust exposure photo.jpg /output --ev +0.5 --width 1920 --format jpg
```

---

## Database Queries

```bash
# Find images by camera
cli-anything-darktable --json library list --camera "Sony" -n 20

# Find high-ISO images
cli-anything-darktable --json library list --iso-min 3200

# Check image edit history
cli-anything-darktable history show 42

# Find images with tags
cli-anything-darktable tags images "landscape"
```

---

## Troubleshooting

**LUT has no effect:**
- Check CUBE file is valid: `cli-anything-darktable lut validate file.cube`
- Verify `--colorspace` matches LUT source (usually sRGB)

**Exposure too bright/dark:**
- Use smaller EV values: `--ev +0.3` instead of `--ev +2.0`
- Check image histogram in darktable GUI

**Colors look wrong:**
- Reset color balance: don't pass color params you don't need
- Check white balance first in darktable GUI

**Output file too large:**
- Use `--format jpg` for smaller files
- Add `--width 1920` to resize
