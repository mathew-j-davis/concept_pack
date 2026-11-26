# Advanced Features for Table-Based Diagrams

This guide covers advanced features for customizing table-based architecture diagrams.

## Table of Contents
1. [Background Nodes](#background-nodes)
2. [Variable Spacing](#variable-spacing)
3. [Color Gradients](#color-gradients)

## Background Nodes

Background nodes create styled rectangles behind groups of cells. They're useful for:
- Visually grouping related content
- Adding subtle borders or highlights
- Creating layered visual effects

### Row-Level Background

Add a `background` field to any row to create a background node behind all cells in that row:

```yaml
rows:
  - height: auto
    background: transparent_bg  # Style name from config
    columns:
      - cell: { label: "Item 1" }
      - cell: { label: "Item 2" }
      - cell: { label: "Item 3" }
```

The background node will automatically:
- Position itself at the top-left of the first cell
- Extend to the bottom-right of the last cell
- Render behind all content (z_index: -1)

### Background Styles

Define background styles in your config file:

```yaml
colors:
  transparent_bg:
    edge: 'E0E0E0'      # Light gray border
    fill: 'FFFFFF'       # White fill
    stroke_width: 1

  highlight_bg:
    edge: 'FFA500'       # Orange border
    fill: 'FFF5E6'       # Light orange fill
    stroke_width: 2
```

### Inline Background Styles

You can also define background styles inline:

```yaml
rows:
  - height: auto
    background:
      edge: 'E0E0E0'
      fill: 'F5F5F5'
      stroke_width: 1
    columns:
      - cell: { label: "Content" }
```

## Variable Spacing

Control the spacing between cells at multiple levels for precise layout control.

### Table-Level Spacing (Default)

```yaml
table:
  spacing: 0.2  # Applied to all rows and columns
  rows:
    - columns:
        - cell: { label: "A" }
        - cell: { label: "B" }  # 0.2cm gap before this
```

### Row-Level Spacing Override

Override spacing for a specific row:

```yaml
rows:
  - height: auto
    spacing: 0.5  # Larger gap between columns in this row
    columns:
      - cell: { label: "Wide" }
      - cell: { label: "Gaps" }  # 0.5cm gap before this

  - height: auto
    spacing: 0.1  # Tighter spacing in this row
    columns:
      - cell: { label: "Tight" }
      - cell: { label: "Fit" }  # 0.1cm gap before this
```

### Column-Level Spacing Override

Override spacing for a specific column:

```yaml
rows:
  - columns:
      - cell: { label: "A" }
      - spacing: 1.0  # Extra space before next column
        cell: { label: "B" }
      - cell: { label: "C" }  # Uses row/table spacing
```

### Spacing Cascade

Spacing resolves with this priority:
1. **Column spacing** (`column.spacing`)
2. **Row spacing** (`row.spacing`)
3. **Table spacing** (`table.spacing`)
4. **Default spacing** (from config: 0.2cm)

```yaml
table:
  spacing: 0.2        # Default for all
  rows:
    - spacing: 0.3    # Override for this row
      columns:
        - cell: { label: "A" }
        - spacing: 0.5  # Override for this column
          cell: { label: "B" }
        - cell: { label: "C" }  # Uses row spacing (0.3)
```

## Color Gradients

Create visual hierarchies and transitions using color gradients across rows.

### Azure-to-Green Gradient Example

The config includes a built-in azure-to-green gradient for technology layers:

```yaml
# In conceptual-arch-config.yaml
colors:
  tech_azure:
    fill: '4A90D9'  # Azure blue
    text: 'FFFFFF'

  tech_teal:
    fill: '3D9999'  # Teal
    text: 'FFFFFF'

  tech_mint:
    fill: '3DA37A'  # Mint green
    text: 'FFFFFF'

  tech_green:
    fill: '3DAD5B'  # Green
    text: 'FFFFFF'
```

### Applying Gradient to Rows

Apply different colors to each row to create a gradient effect:

```yaml
rows:
  # Row 1: Azure
  - height: auto
    style: tech_azure  # Applied to all cells in row
    columns:
      - cell: { label: "Service A", style: tech_azure }
      - cell: { label: "Service B", style: tech_azure }

  # Row 2: Teal
  - height: auto
    style: tech_teal
    columns:
      - cell: { label: "Platform A", style: tech_teal }
      - cell: { label: "Platform B", style: tech_teal }

  # Row 3: Green
  - height: auto
    style: tech_green
    columns:
      - cell: { label: "Tool 1", style: tech_green }
      - cell: { label: "Tool 2", style: tech_green }
```

### Creating Custom Gradients

Define your own color gradient:

```yaml
# In your diagram-config.yaml
colors:
  gradient_light:
    fill: 'E3F2FD'  # Light blue
    text: '000000'

  gradient_medium:
    fill: '90CAF9'  # Medium blue
    text: '000000'

  gradient_dark:
    fill: '1976D2'  # Dark blue
    text: 'FFFFFF'
```

Then apply to rows:

```yaml
rows:
  - style: gradient_light
    columns: [...]
  - style: gradient_medium
    columns: [...]
  - style: gradient_dark
    columns: [...]
```

## Combining Features

You can combine all these features for sophisticated layouts:

```yaml
table:
  spacing: 0.2
  rows:
    # Highlighted row with custom spacing and gradient color
    - height: auto
      spacing: 0.3
      style: tech_azure
      background: transparent_bg
      columns:
        - cell: { label: "Important", style: tech_azure }
        - spacing: 0.5  # Extra space before next column
          cell: { label: "Items", style: tech_azure }
        - cell: { label: "Here", style: tech_azure }
```

## Tips

✅ **DO:**
- Use background nodes sparingly for emphasis
- Choose gradual color transitions for smooth gradients
- Use variable spacing to create visual separation between sections
- Test colors for readability (white text on dark, black on light)

❌ **DON'T:**
- Overuse background nodes (can create visual clutter)
- Use jarring color transitions (e.g., blue → red)
- Make spacing too large (breaks visual connection)
- Use low-contrast color combinations

## Examples

See `example_concept_pack/diagram-definitions/example-architecture.yaml` for working examples of:
- Technology layer gradients (azure → teal → green)
- Variable spacing between sections
- Mixed styling approaches
