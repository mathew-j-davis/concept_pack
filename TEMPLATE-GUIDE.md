# PowerPoint Template Guide

The clean_template.pptx provides a neutral, professional template for concept pack presentations without any organizational branding.

## Template Slides

### Slide 1: Title Slide
**Purpose**: Opening slide with presentation title, subtitle, author, and date

**Placeholders**:
- `{{title}}` - Main presentation title (44pt, blue, centered)
- `{{subtitle}}` - Subtitle or description (24pt, light blue, centered)
- `{{author}}` - Author name (14pt, gray, centered)
- `{{date}}` - Presentation date (14pt, gray, centered)

**Usage in Markdown**:
```markdown
# My Presentation
slide-type:: title-slide
title:: Enterprise Architecture Overview
subtitle:: Q4 2024 Technical Review
author:: Architecture Team
date:: 2024-11-26
```

### Slide 2: Executive Summary
**Purpose**: Executive decision slide with status indicators and recommendation

**Placeholders**:
- `{{opportunity-name}}` - Project/opportunity name
- `{{opportunity-number}}` - Reference number
- `{{opportunity-recommendation}}` - Recommendation text box
- `{{roadmap-fit}}` - Status indicator (with topbar-color)
- `{{design-effort}}` - Status indicator (with topbar-color)
- `{{tech-identified}}` - Status indicator (with topbar-color)
- `{{governance}}` - Status indicator (with topbar-color)
- `{{decision-requested}}` - Decision box (with fill and text-color)

**Usage in Markdown**:
```markdown
# Executive Summary
slide-type:: executive-summary

opportunity-name:: Cloud Migration Phase 1
opportunity-number:: OD-2024-105

opportunity-recommendation::
Migrate core services to cloud infrastructure using a phased approach.
::end

roadmap-fit:: On-roadmap
roadmap-fit-topbar-color:: 00B050

design-effort:: Moderate
design-effort-topbar-color:: FFC000

tech-identified:: All identified
tech-identified-topbar-color:: 00B050

governance:: Light-touch TDA
governance-topbar-color:: 00B050

decision-requested:: Endorse
decision-requested-fill:: 00A79D
decision-requested-text-color:: FFFFFF
```

### Slide 3: Concept Slide
**Purpose**: Content slide for concept explanations (similar to text-slide)

**Placeholders**:
- `{{title}}` - Slide title (32pt, blue)
- `{{category}}` - Optional category/section label (12pt, light blue)
- `{{text}}` - Main content area (16pt)

### Slide 4: Table Slide
**Purpose**: Display data in tabular format

**Placeholders**:
- `{{title}}` - Slide title
- `{{category}}` - Optional category
- Table with 5 columns × 4 rows (placeholder, dynamically replaced)

**Usage in Markdown**:
```markdown
# Technology Stack
slide-type:: table
table-style:: technology-stack

| Capability | Layer | Technology | Status | Notes |
|------------|-------|------------|--------|-------|
| Container Platform | Infrastructure | AWS ECS | Reuse | Standard |
| Database | Data | PostgreSQL | Reuse | Managed |
| Cache | Data | Redis | New | Performance |
```

### Slide 5: Tech Gaps Slide
**Purpose**: Document technology gaps and missing capabilities

**Placeholders**:
- Title: "Technology Gaps" (pre-filled)
- `{{gaps-content}}` - Gap descriptions (14pt)

### Slide 6: Design Group Slide
**Purpose**: Document design groups and architectural decisions

**Placeholders**:
- Title: "Design Groups" (pre-filled)
- `{{design-groups}}` - Design group content (14pt)

### Slide 7: Governance Slide
**Purpose**: Document governance requirements and approach

**Placeholders**:
- Title: "Governance" (pre-filled)
- `{{governance-content}}` - Governance details (14pt)

### Slide 8: Text Slide
**Purpose**: Standard content slide with bullets or paragraphs

**Placeholders**:
- `{{title}}` - Slide title (32pt, blue)
- `{{category}}` - Optional category/section label (12pt, light blue)
- `{{text}}` - Main content area (16pt)

**Usage in Markdown**:
```markdown
# Key Components
slide-type:: text-slide
title:: Architecture Layers
category:: Technical

text::
## Presentation Layer
- Web UI for browser access
- Mobile App for iOS/Android
- API Gateway for integrations

## Business Logic
- Order Service for transactions
- User Service for accounts
::end
```

**Markdown Formatting Support**:
- `**bold text**` - Bold
- `*italic text*` - Italic
- `# Header` - Header (bold, same size)
- `## Subheader` - Subheader (bold, same size)
- `- Bullet` - Bullet point
- `  - Sub-bullet` - Sub-bullet (indented)

### Slide 9: Image Slide
**Purpose**: Display diagrams and images

**Placeholders**:
- `{{title}}` - Slide title (32pt, blue)
- `{{category}}` - Optional category (12pt, light blue)
- `{{image}}` - Image file path (automatically replaced with actual image)

**Usage in Markdown**:
```markdown
# System Architecture
slide-type:: image-slide
title:: Conceptual Architecture
category:: Architecture
image:: output/architecture.png
image-width:: 9.5
```

### Slide 10: Section Slide
**Purpose**: Section divider / chapter slide

**Placeholders**:
- `{{title}}` - Large centered title (44pt, blue)
- `{{subtitle}}` - Subtitle below title (20pt, light blue)

**Usage in Markdown**:
```markdown
# Section Break
slide-type:: section-slide
title:: Part 2: Implementation
subtitle:: Technical Details
```

## Color Palette

The template uses a neutral, professional color scheme:

- **Brand Blue** (#1F4A70) - Primary color for titles and headers
- **Brand Light** (#2E5C8A) - Secondary color for subtitles and accents
- **Accent Teal** (#00A79D) - Decision boxes and highlights
- **Gray Dark** (#404040) - Body text
- **Gray Light** (#F2F2F2) - Backgrounds and separators
- **White** (#FFFFFF) - Slide backgrounds and contrast

## Customizing the Template

### Method 1: Edit the Template Directly
Open `clean_template.pptx` in PowerPoint and customize:
- Colors (change all instances to match your brand)
- Fonts (change font family)
- Layout (adjust text box positions and sizes)
- Add logos or branding elements

### Method 2: Regenerate from Script
Edit `create-clean-template.py` and change:
- Color constants at the top
- Font sizes and styles
- Layout dimensions
- Add additional placeholders

Then run:
```bash
python3 create-clean-template.py
```

### Method 3: Use Your Own Template
1. Create a PowerPoint with the same 10 slides
2. Use the placeholder text formats ({{field-name}})
3. Update `template-config.yaml` to point to your template
4. Ensure slide order matches the config

## Template Configuration

Edit `clean-template-config.yaml` to:
- Change which slide number corresponds to which type
- Modify table styling rules
- Add custom table styles for your data

## Table Styling

Tables support conditional formatting based on cell values:

```yaml
table_styles:
  my-table-style:
    Status:  # Column name
      style_by_value:
        Complete:
          fill: "00B050"  # Green
          text_color: "FFFFFF"
        In Progress:
          fill: "FFC000"  # Orange
          text_color: "000000"
        Not Started:
          fill: "F6ECEC"  # Light red
          text_color: "000000"
```

Use in markdown:
```markdown
slide-type:: table
table-style:: my-table-style
```

## Best Practices

1. **Consistent Sizing**: Keep slide content within the margins (0.5" from edges)
2. **Font Hierarchy**: 
   - Titles: 32-44pt
   - Subtitles/Categories: 12-24pt
   - Body: 14-18pt
3. **Color Usage**: Use brand colors for structure, not content
4. **Image Quality**: Use high-DPI images (300dpi recommended)
5. **Text Amount**: Keep slides concise - maximum 5-7 bullets per slide

## Troubleshooting

### Placeholders not replaced
- Check that placeholder text uses `{{double-braces}}`
- Verify the field name matches what's in your markdown
- Ensure slide type matches in template-config.yaml

### Wrong slide layout used
- Check slide order in template matches config
- Verify slide-type:: in markdown matches a configured type
- Count slides (should be 10)

### Styling not applied
- Check table-style:: name matches config
- Verify column names match exactly (case-sensitive)
- Ensure value strings match exactly

### Images not appearing
- Check image path is correct relative to working directory
- Verify image file exists
- Try image-width:: parameter to adjust size

## Examples

See `example-concept-pack.md` for a complete working example using all slide types.

## License

MIT - Use freely for any purpose, commercial or personal.
