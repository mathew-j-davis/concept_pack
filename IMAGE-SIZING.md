# Image Sizing in Presentations

Control the size of images on image slides with per-image configuration.

## Default Behavior

Without custom sizing, images use sensible defaults:

**With placeholder** (template has an existing picture):
- Fits within the placeholder bounds
- Maintains aspect ratio
- Centers if smaller than placeholder

**Without placeholder** (auto-sizing):
- Maximum width: 8 inches
- Maximum height: 5.5 inches
- Maintains aspect ratio
- Centers on slide

## Custom Sizing (Per Image)

Override the default size for any image using markdown fields:

```markdown
# System Architecture
slide-type:: image-slide
title:: Conceptual Architecture
image:: output/architecture.png
image-width:: 9
image-height:: 6
```

### Fields

- **`image-width::`** - Width in inches (decimal numbers supported)
- **`image-height::`** - Height in inches (decimal numbers supported)

Both fields are **optional** and work differently depending on what you specify:

**Specify ONE dimension = Proportional scaling:**
```markdown
# Wide Diagram - scales to 9.5" wide, height calculated from aspect ratio
image:: diagrams/wide.png
image-width:: 9.5          # Height scales proportionally

# Tall Diagram - scales to 7" tall, width calculated from aspect ratio
image:: diagrams/tall.png
image-height:: 7           # Width scales proportionally
```

**Specify BOTH dimensions = Constrained to fit within bounds:**
```markdown
# Custom Both - fits within 8.5" × 6.5" box, maintaining aspect ratio
image:: diagrams/custom.png
image-width:: 8.5
image-height:: 6.5         # Fits within both constraints
```

## How Sizing Works

1. **Aspect ratio is always maintained** - images never stretch or squash
2. **One dimension = proportional scaling**:
   - Specify only `image-width` → scales to that width, height calculated from aspect ratio
   - Specify only `image-height` → scales to that height, width calculated from aspect ratio
3. **Both dimensions = constrained fit**:
   - Image fits within the specified width AND height
   - Actual size may be smaller to maintain aspect ratio
4. **Centered automatically** - positioned in the center of the slide

## Examples

### Default Size (8" × 5.5")
```markdown
image:: output/diagram.png
```

### Larger Image (9" × 6")
```markdown
image:: output/diagram.png
image-width:: 9
image-height:: 6
```

### Extra Wide (proportional from width)
```markdown
image:: output/wide-diagram.png
image-width:: 9.5
```
✅ **Proportional scaling**: Exactly 9.5" wide, height calculated from aspect ratio.

### Extra Tall (proportional from height)
```markdown
image:: output/tall-diagram.png
image-height:: 7
```
✅ **Proportional scaling**: Exactly 7" tall, width calculated from aspect ratio.

### Maximum Slide Coverage (constrained fit)
```markdown
image:: output/large-diagram.png
image-width:: 9.5
image-height:: 7
```
⚠️ **Constrained fit**: Image fits within 9.5" × 7" box. Final size depends on aspect ratio - may be smaller than 9.5" × 7".

## Typical Sizes

PowerPoint slides are **10" × 7.5"** (standard 4:3 aspect ratio).

**Recommended maximums:**
- **Width**: 9.5 inches (leaves 0.25" margin on each side)
- **Height**: 7 inches (leaves room for title and margins)

**Common use cases:**
- **Full width diagrams**: `image-width:: 9.5`
- **Tall workflows**: `image-height:: 7`
- **Standard centered**: `image-width:: 8, image-height:: 5.5` (default)
- **Large centered**: `image-width:: 9, image-height:: 6`

## Multiple Images in One Presentation

Each image slide can have different dimensions:

```markdown
---

# Wide Architecture Diagram
slide-type:: image-slide
title:: System Architecture
image:: output/architecture.png
image-width:: 9.5          # Wide

---

# Tall Process Flow
slide-type:: image-slide
title:: Process Flow
image:: output/flow.png
image-height:: 7           # Tall

---

# Standard Diagram
slide-type:: image-slide
title:: Component Diagram
image:: output/components.png
# Uses defaults: 8" × 5.5"
```

## Tips

✅ **DO:** Specify dimensions when you need larger/smaller images
✅ **DO:** Omit dimensions to use sensible defaults
✅ **DO:** Use decimal numbers (9.5, 6.75, etc.)
✅ **DO:** Specify just one dimension if that's the constraint

❌ **DON'T:** Expect exact dimensions - aspect ratio is maintained
❌ **DON'T:** Use dimensions larger than the slide (10" × 7.5")
❌ **DON'T:** Forget to account for title space at the top

## Troubleshooting

**Image appears too small:**
- Increase `image-width` and/or `image-height`
- Remember: actual size respects aspect ratio

**Image appears too large:**
- Decrease `image-width` and/or `image-height`
- Default is usually a good balance

**Image not centered:**
- Check that your image dimensions are reasonable
- Very small dimensions may not center as expected

**Invalid size warning:**
- Check that width/height values are numbers
- Use decimal point for fractions (9.5, not 9 1/2)
