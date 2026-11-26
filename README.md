# Concept Pack

Table-based architecture diagram generator. Write clean YAML table definitions and generate beautifully formatted architecture diagrams.

## Overview

Concept Pack provides an intuitive table-based approach to creating architecture diagrams. Instead of positioning each element manually, you define your architecture as nested tables with rows and columns. The generator handles all the positioning, spacing, and layout automatically.

## Features

- **Table-based layout** - Intuitive rows and columns structure
- **Nested tables** - Create complex layouts with recursive nesting
- **Auto-sizing** - Automatic height and width calculations
- **Variable spacing** - Control gaps between elements at multiple levels
- **Background colors** - Add backgrounds to entire rows or columns
- **Gradient colors** - Smooth color transitions across layers
- **Icon support** - Embed SVG icons in cells with dual layout modes
- **Style system** - Reusable color schemes and typography

## Installation

No build required - runs directly with Python 3:

```bash
git clone https://github.com/YOUR-USERNAME/concept_pack.git
cd concept_pack
```

Requirements:
- Python 3.7+
- PyYAML (usually pre-installed)

## Quick Start

### 1. Create a table definition

```yaml
# architecture.yaml
table:
  width: 46.6
  height: 20.0
  spacing: 0.1
  
  rows:
    - height: auto
      columns:
        # Users column
        - width: 8.0
          cells_stack:
            - label: "USERS"
              style: header
              height: 2.0
            - label: "Customers"
              height: auto
            - label: "Staff"
              height: auto

        # Application layers
        - width: auto
          table:
            column_widths: [8.0, auto]
            rows:
              # Presentation Layer
              - height: auto
                columns:
                  - cell:
                      label: "PRESENTATION"
                      style: header
                  - table:
                      rows:
                        - height: auto
                          columns:
                            - cell:
                                label: "Web UI"
                            - cell:
                                label: "Mobile App"
                            - cell:
                                label: "API Gateway"
```

### 2. Generate the diagram

```bash
python3 table-to-diagram.py architecture.yaml output.yaml
```

This produces a positioned YAML file ready for boxesandarrows.

### 3. Render to SVG

```bash
# Requires boxesandarrows (https://github.com/mathew-j-davis/boxesandarrows)
node ../boxesandarrows/src/index.js -y output.yaml -r svg -o diagram
```

Creates `diagram.svg` - a beautiful architecture diagram!

## Key Concepts

### cells_stack vs table

**cells_stack** - Simple vertical stack (1D):
```yaml
cells_stack:
  - label: "Header"
    height: 2.0
  - label: "Item 1"
    height: auto
  - label: "Item 2"
    height: auto
```

**table** - Rows and columns (2D):
```yaml
table:
  rows:
    - height: auto
      columns:
        - width: 8.0
          cell: { label: "Left" }
        - width: auto
          cell: { label: "Right" }
```

### Auto-sizing

Use `auto` for dynamic sizing:

```yaml
# Fixed width, auto height
- width: 8.0
  height: auto

# Auto width fills remaining space
- width: auto
  height: 5.0
```

### Spacing

Control gaps at multiple levels:

```yaml
table:
  spacing: 0.1  # Default for whole table
  rows:
    - spacing: 0.5  # Override for this row
      columns:
        - spacing: 0.2  # Override for this column
```

### Backgrounds

Add colored backgrounds to rows or columns:

```yaml
columns:
  - width: 8.0
    background: dark_navy_bg  # Style name from config
    cells_stack: [...]
```

### Icons

Add icons to cells with automatic layout:

```yaml
# Regular cell: icon at top, text below
- cell:
    label: "Web UI"
    icon: "icons/web.svg"

# Header cell: icon on left, text centered
- cell:
    label: "PRESENTATION"
    style: header
    icon: "icons/presentation.svg"
```

## Style Configuration

Create a config file for colors and styles:

```yaml
# diagram-config.yaml
colors:
  header: '#1F4A70'
  default: '#2E5C8A'
  foundation: '#7FA8C9'
  dark_navy_bg: '#1A2332'

styles:
  font_size: 18
  font_weight: 500
  font_family: 'Arial, sans-serif'
  
  header:
    font_size: 20
    font_weight: 700
    fill: '#1F4A70'
    textcolor: '#FFFFFF'
```

Pass it to the generator:

```bash
python3 table-to-diagram.py \
  architecture.yaml \
  output.yaml \
  --config diagram-config.yaml
```

## Documentation

- **[ADVANCED-FEATURES.md](ADVANCED-FEATURES.md)** - Backgrounds, gradients, variable spacing
- **[STYLING-GUIDE.md](STYLING-GUIDE.md)** - Color schemes and typography
- **[MARKDOWN-SUPPORT.md](MARKDOWN-SUPPORT.md)** - Markdown to PowerPoint (legacy)
- **[IMAGE-SIZING.md](IMAGE-SIZING.md)** - Working with images

## Complete Example

See [../example_architecture_template/](../example_architecture_template/) for a complete working project with:
- Build automation
- Icon library
- PNG generation
- Live-reload development

## Integration with BoxesAndArrows

Concept Pack generates YAML that boxesandarrows understands:

```bash
# Option 1: Two-step process
python3 ../concept_pack/table-to-diagram.py diagram.yaml positioned.yaml
node ../boxesandarrows/src/index.js -y positioned.yaml -r svg -o output

# Option 2: One-liner with shell
python3 ../concept_pack/table-to-diagram.py diagram.yaml positioned.yaml && \
  node ../boxesandarrows/src/index.js -y positioned.yaml -r svg -o output
```

## Command Line Options

```bash
python3 table-to-diagram.py <input.yaml> <output.yaml> [options]

Options:
  --config <file>    Style configuration file
  --help            Show help message
```

## Examples

### Three-tier Architecture
```yaml
rows:
  - columns:
      - { label: "Users" }
      - table:
          rows:
            - { label: "Frontend" }
            - { label: "Backend" }
            - { label: "Database" }
      - { label: "External" }
```

### Microservices
```yaml
rows:
  - columns:
      - cells_stack:
          - { label: "API Gateway" }
          - { label: "Service Mesh" }
      - table:
          column_widths: [auto, auto, auto]
          rows:
            - columns:
                - { label: "Service A" }
                - { label: "Service B" }
                - { label: "Service C" }
```

## Troubleshooting

### "Module not found: yaml"
Install PyYAML:
```bash
pip3 install pyyaml
```

### "Invalid YAML syntax"
Check your YAML indentation - must be consistent (2 or 4 spaces).

### "Width/height too small"
Make sure your table dimensions accommodate all content with spacing.

### Icons not showing
Make sure icon paths start with `./` or are absolute:
```yaml
icon: "./icons/icon.svg"  # ✅ Correct
icon: "icons/icon.svg"    # ❌ Won't work
```

## Related Projects

- **[boxesandarrows](https://github.com/mathew-j-davis/boxesandarrows)** - SVG rendering engine
- **[boxwatcher](https://github.com/YOUR-USERNAME/boxwatcher)** - Build automation
- **[example template](https://github.com/YOUR-USERNAME/architecture-diagram-template)** - Starter project

## License

MIT

## Contributing

Issues and pull requests welcome!
