# Color Grading Reference Guide

## Color Wheel Basics

- **Hue**: Color angle (0-360°) - Red=0, Green=120, Blue=240
- **Chroma**: Color intensity (0-1) - 0=grey, 1=saturated
- **Luminance**: Brightness (-1 to 1) - negative=dark, positive=bright

## Darktable Color Balance RGB Module

The `colorbalancergb` module controls color in 4 tonal regions:

| Region | Luminance Range | Typical Use |
|--------|----------------|-------------|
| Shadows | 0-30% | Deep shadows, dark areas |
| Midtones | 30-70% | Main subject, skin tones |
| Highlights | 70-100% | Bright areas, sky |
| Global | 0-100% | Overall color shift |

### Parameters

- `shadows/midtones/highlights_H`: Hue angle (0-360)
- `shadows/midtones/highlights_C`: Chroma/saturation (0-1)
- `shadows/midtones/highlights_Y`: Luminance shift (-1 to 1)
- `global_saturation`: Overall saturation (-1 to 1)
- `contrast`: Tonal contrast (-1 to 1)
- `vibrance`: Smart saturation (-1 to 1)

## Film Stock Emulation

### Kodak Portra 400
- Warm skin tones, low contrast
- Shadows: slight warm shift (H=30, C=0.1)
- Highlights: neutral to warm (H=40, C=0.05)
- Saturation: -0.1 overall

### Kodak Ektar 100
- Vivid colors, high saturation
- Shadows: cool blue (H=210, C=0.15)
- Highlights: warm (H=40, C=0.1)
- Saturation: +0.2 overall

### Fuji Velvia 50
- Ultra vivid, high contrast
- Shadows: deep blue-green (H=180, C=0.2)
- Highlights: warm yellow (H=50, C=0.15)
- Contrast: +0.3
- Saturation: +0.3

### Fuji Pro 400H
- Soft, pastel, lifted shadows
- Shadows: teal (H=190, C=0.2)
- Highlights: warm pink (H=350, C=0.1)
- Saturation: -0.15

### Kodak Tri-X 400 (B&W)
- High contrast, visible grain
- Apply B&W LUT
- Contrast: +0.3
- Black point: +0.02

## Cinematic Color Grades

### Teal & Orange (Hollywood Blockbuster)
Used in: Action movies, Transformers, Mad Max
```
shadows: H=190, C=0.4 (teal)
highlights: H=30, C=0.3 (orange)
global_saturation: +0.1
```

### Bleach Bypass (Saving Private Ryan)
Used in: War films, gritty dramas
```
global_saturation: -0.5
contrast: +0.4
brilliance_global: +0.2
```

### Day for Night
Used in: Night scenes shot during day
```
exposure: -1.5
shadows: H=220, C=0.3 (blue)
global_saturation: -0.3
contrast: +0.2
```

### Warm Vintage (Nostalgic)
Used in: Period films, flashbacks
```
shadows: H=40, C=0.2 (warm brown)
highlights: H=50, C=0.15 (warm yellow)
global_saturation: -0.2
curve_preset: film_fade
```

### Cold Modern (Sci-fi)
Used in: Sci-fi, thriller
```
shadows: H=220, C=0.3 (cold blue)
highlights: H=200, C=0.1 (slightly blue)
global_saturation: -0.1
contrast: +0.2
```

## Curve Techniques

### S-Curve (Contrast Boost)
```
Points: (0,0), (0.25,0.18), (0.5,0.5), (0.75,0.82), (1,1)
Effect: Darker shadows, brighter highlights
```

### Lifted Blacks (Faded Film)
```
Points: (0,0.08), (0.3,0.3), (0.7,0.72), (1,1)
Effect: Washed out shadows, vintage feel
```

### Crushed Highlights (Matte)
```
Points: (0,0), (0.3,0.3), (0.7,0.65), (1,0.88)
Effect: Dull whites, flat look
```

### Cross Process
```
R: (0,0), (0.25,0.15), (0.5,0.55), (0.75,0.85), (1,1)
G: (0,0), (0.25,0.3), (0.5,0.5), (0.75,0.7), (1,1)
B: (0,0.05), (0.25,0.2), (0.5,0.45), (0.75,0.75), (1,0.95)
Effect: Color shifts, film processing errors
```

## Exposure Values (EV)

| EV Change | Effect | Use Case |
|-----------|--------|----------|
| -2.0 | 4x darker | Heavy underexposure |
| -1.0 | 2x darker | Slight underexposure |
| -0.3 | Slightly darker | Subtle darken |
| 0.0 | No change | Correct exposure |
| +0.3 | Slightly brighter | Subtle brighten |
| +0.7 | ~1.5x brighter | Standard correction |
| +1.0 | 2x brighter | One stop over |
| +2.0 | 4x brighter | Heavy overexposure |

## Workflow Order

1. **White Balance** - Correct color temperature
2. **Exposure** - Set overall brightness
3. **Tone Curve** - Adjust contrast and tonal range
4. **Color Balance** - Color grade shadows/midtones/highlights
5. **LUT** - Apply film emulation or creative look
6. **Final Adjustments** - Saturation, vibrance, fine-tuning
