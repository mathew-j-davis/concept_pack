#!/usr/bin/env python3
"""
Create a clean PowerPoint template without organizational branding.

This creates a minimal template with all required slide layouts:
1. title-slide
2. executive-summary
3. concept-slide
4. table
5. tech-gaps-slide
6. design-group-slide
7. governance-slide
8. text-slide
9. image-slide
10. section-slide
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# Standard slide dimensions (widescreen 16:9)
SLIDE_WIDTH = Inches(10)
SLIDE_HEIGHT = Inches(7.5)

# Color palette - neutral professional colors
BRAND_BLUE = RGBColor(31, 74, 112)      # #1F4A70
BRAND_LIGHT = RGBColor(46, 92, 138)     # #2E5C8A
ACCENT_TEAL = RGBColor(0, 167, 157)     # #00A79D
GRAY_DARK = RGBColor(64, 64, 64)        # #404040
GRAY_LIGHT = RGBColor(242, 242, 242)    # #F2F2F2
WHITE = RGBColor(255, 255, 255)         # #FFFFFF

def set_shape_color(shape, fill_color, text_color=None):
    """Set shape fill and text color."""
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if text_color and hasattr(shape, 'text_frame'):
        for paragraph in shape.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.color.rgb = text_color

def add_text_box(slide, left, top, width, height, text, font_size=18, bold=False,
                 color=GRAY_DARK, alignment=PP_ALIGN.LEFT, placeholder_text=None):
    """Add a text box to a slide."""
    textbox = slide.shapes.add_textbox(left, top, width, height)
    text_frame = textbox.text_frame
    text_frame.word_wrap = True
    text_frame.vertical_anchor = MSO_ANCHOR.TOP

    p = text_frame.paragraphs[0]
    p.alignment = alignment
    p.text = placeholder_text or text

    run = p.runs[0]
    run.font.size = Pt(font_size)
    run.font.name = 'Arial'
    run.font.bold = bold
    run.font.color.rgb = color

    return textbox

def create_title_slide(prs):
    """Slide 1: Title Slide"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout

    # Title
    add_text_box(slide, Inches(0.5), Inches(2.5), Inches(9), Inches(1),
                 "{{title}}", font_size=44, bold=True, color=BRAND_BLUE,
                 alignment=PP_ALIGN.CENTER)

    # Subtitle
    add_text_box(slide, Inches(0.5), Inches(3.8), Inches(9), Inches(0.6),
                 "{{subtitle}}", font_size=24, color=BRAND_LIGHT,
                 alignment=PP_ALIGN.CENTER)

    # Author
    add_text_box(slide, Inches(0.5), Inches(5), Inches(9), Inches(0.4),
                 "{{author}}", font_size=14, color=GRAY_DARK,
                 alignment=PP_ALIGN.CENTER)

    # Date
    add_text_box(slide, Inches(0.5), Inches(5.5), Inches(9), Inches(0.4),
                 "{{date}}", font_size=14, color=GRAY_DARK,
                 alignment=PP_ALIGN.CENTER)

def create_executive_summary_slide(prs):
    """Slide 2: Executive Summary with status indicators"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Title
    add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.5),
                 "Executive Summary", font_size=32, bold=True, color=BRAND_BLUE)

    # Opportunity info
    add_text_box(slide, Inches(0.5), Inches(1.2), Inches(4), Inches(0.3),
                 "{{opportunity-name}}", font_size=12, bold=True)
    add_text_box(slide, Inches(5), Inches(1.2), Inches(4), Inches(0.3),
                 "{{opportunity-number}}", font_size=12, bold=True)

    # Recommendation box
    recommendation = slide.shapes.add_shape(
        1,  # Rectangle
        Inches(0.5), Inches(1.7), Inches(9), Inches(2)
    )
    set_shape_color(recommendation, GRAY_LIGHT)
    tf = recommendation.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.2)
    tf.margin_right = Inches(0.2)
    tf.margin_top = Inches(0.1)
    p = tf.paragraphs[0]
    p.text = "{{opportunity-recommendation}}"
    p.font.size = Pt(14)

    # Status indicators (top bars with text)
    y_pos = Inches(4.2)
    indicators = [
        ("{{roadmap-fit}}", "Roadmap Fit"),
        ("{{design-effort}}", "Design Effort"),
        ("{{tech-identified}}", "Tech Identified"),
        ("{{governance}}", "Governance"),
    ]

    for i, (value_text, label_text) in enumerate(indicators):
        x_pos = Inches(0.5 + i * 2.3)

        # Top colored bar (placeholder for topbar-color)
        bar = slide.shapes.add_shape(
            1,  # Rectangle
            x_pos, y_pos, Inches(2), Inches(0.15)
        )
        set_shape_color(bar, BRAND_LIGHT)

        # Value box
        value_box = add_text_box(slide, x_pos, y_pos + Inches(0.15),
                                Inches(2), Inches(0.4),
                                value_text, font_size=12, bold=True,
                                alignment=PP_ALIGN.CENTER)

        # Label
        add_text_box(slide, x_pos, y_pos + Inches(0.6), Inches(2), Inches(0.3),
                    label_text, font_size=10, color=GRAY_DARK,
                    alignment=PP_ALIGN.CENTER)

    # Decision box
    decision = slide.shapes.add_shape(
        1,  # Rectangle
        Inches(0.5), Inches(5.5), Inches(9), Inches(1.3)
    )
    set_shape_color(decision, ACCENT_TEAL, WHITE)
    tf = decision.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "Decision Requested: {{decision-requested}}"
    p.font.size = Pt(20)
    p.font.bold = True

def create_concept_slide(prs):
    """Slide 3: Concept Slide (similar to text slide with sections)"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Title
    add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.5),
                 "{{title}}", font_size=32, bold=True, color=BRAND_BLUE)

    # Category (optional)
    add_text_box(slide, Inches(0.5), Inches(0.95), Inches(9), Inches(0.3),
                 "{{category}}", font_size=12, color=BRAND_LIGHT)

    # Content area
    add_text_box(slide, Inches(0.5), Inches(1.5), Inches(9), Inches(5.5),
                 "{{text}}", font_size=16, placeholder_text="Concept content here...")

def create_table_slide(prs):
    """Slide 4: Table Slide"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Title
    add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.5),
                 "{{title}}", font_size=32, bold=True, color=BRAND_BLUE)

    # Category (optional)
    add_text_box(slide, Inches(0.5), Inches(0.95), Inches(9), Inches(0.3),
                 "{{category}}", font_size=12, color=BRAND_LIGHT)

    # Table placeholder (5 columns × 4 rows)
    rows, cols = 4, 5
    left = Inches(0.5)
    top = Inches(1.5)
    width = Inches(9)
    height = Inches(3)

    table = slide.shapes.add_table(rows, cols, left, top, width, height).table

    # Set header row style
    for cell in table.rows[0].cells:
        set_shape_color(cell, BRAND_LIGHT, WHITE)
        cell.text_frame.paragraphs[0].font.bold = True
        cell.text_frame.paragraphs[0].font.size = Pt(12)

    # Set data row style
    for row_idx in range(1, rows):
        for cell in table.rows[row_idx].cells:
            set_shape_color(cell, WHITE, GRAY_DARK)
            cell.text_frame.paragraphs[0].font.size = Pt(11)

def create_tech_gaps_slide(prs):
    """Slide 5: Tech Gaps Slide"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Title
    add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.5),
                 "Technology Gaps", font_size=32, bold=True, color=BRAND_BLUE)

    # Content
    add_text_box(slide, Inches(0.5), Inches(1.2), Inches(9), Inches(5.8),
                 "{{gaps-content}}", font_size=14,
                 placeholder_text="• Technology gap 1\n• Technology gap 2\n• Technology gap 3")

def create_design_group_slide(prs):
    """Slide 6: Design Group Slide"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Title
    add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.5),
                 "Design Groups", font_size=32, bold=True, color=BRAND_BLUE)

    # Content
    add_text_box(slide, Inches(0.5), Inches(1.2), Inches(9), Inches(5.8),
                 "{{design-groups}}", font_size=14,
                 placeholder_text="Design group information...")

def create_governance_slide(prs):
    """Slide 7: Governance Slide"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Title
    add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.5),
                 "Governance", font_size=32, bold=True, color=BRAND_BLUE)

    # Content
    add_text_box(slide, Inches(0.5), Inches(1.2), Inches(9), Inches(5.8),
                 "{{governance-content}}", font_size=14,
                 placeholder_text="Governance requirements and approach...")

def create_text_slide(prs):
    """Slide 8: Text Slide (standard content slide)"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Title
    add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.5),
                 "{{title}}", font_size=32, bold=True, color=BRAND_BLUE)

    # Category (optional, smaller subtitle)
    add_text_box(slide, Inches(0.5), Inches(0.95), Inches(9), Inches(0.3),
                 "{{category}}", font_size=12, color=BRAND_LIGHT)

    # Content area
    add_text_box(slide, Inches(0.5), Inches(1.5), Inches(9), Inches(5.5),
                 "{{text}}", font_size=16,
                 placeholder_text="Bullet points or paragraphs here...\n\n• Point 1\n• Point 2\n• Point 3")

def create_image_slide(prs):
    """Slide 9: Image Slide"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Title
    add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.5),
                 "{{title}}", font_size=32, bold=True, color=BRAND_BLUE)

    # Category (optional)
    add_text_box(slide, Inches(0.5), Inches(0.95), Inches(9), Inches(0.3),
                 "{{category}}", font_size=12, color=BRAND_LIGHT)

    # Image placeholder (gray box)
    image_placeholder = slide.shapes.add_shape(
        1,  # Rectangle
        Inches(0.5), Inches(1.5), Inches(9), Inches(5.5)
    )
    set_shape_color(image_placeholder, GRAY_LIGHT)
    tf = image_placeholder.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "[Image: {{image}}]"
    p.font.size = Pt(18)
    p.font.color.rgb = GRAY_DARK

def create_section_slide(prs):
    """Slide 10: Section Slide (divider/chapter slide)"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Large centered title
    add_text_box(slide, Inches(0.5), Inches(3), Inches(9), Inches(1),
                 "{{title}}", font_size=44, bold=True, color=BRAND_BLUE,
                 alignment=PP_ALIGN.CENTER)

    # Subtitle
    add_text_box(slide, Inches(0.5), Inches(4.2), Inches(9), Inches(0.6),
                 "{{subtitle}}", font_size=20, color=BRAND_LIGHT,
                 alignment=PP_ALIGN.CENTER)

def main():
    """Create the template presentation."""
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT

    print("Creating clean PowerPoint template...")

    # Create all slides
    print("  1. Title Slide")
    create_title_slide(prs)

    print("  2. Executive Summary")
    create_executive_summary_slide(prs)

    print("  3. Concept Slide")
    create_concept_slide(prs)

    print("  4. Table Slide")
    create_table_slide(prs)

    print("  5. Tech Gaps Slide")
    create_tech_gaps_slide(prs)

    print("  6. Design Group Slide")
    create_design_group_slide(prs)

    print("  7. Governance Slide")
    create_governance_slide(prs)

    print("  8. Text Slide")
    create_text_slide(prs)

    print("  9. Image Slide")
    create_image_slide(prs)

    print(" 10. Section Slide")
    create_section_slide(prs)

    # Save
    output_file = "clean_template.pptx"
    prs.save(output_file)
    print(f"\n✅ Template created: {output_file}")
    print(f"   Contains {len(prs.slides)} slides")
    print("\nSlide mapping:")
    print("  1 = title-slide")
    print("  2 = executive-summary")
    print("  3 = concept-slide")
    print("  4 = table")
    print("  5 = tech-gaps-slide")
    print("  6 = design-group-slide")
    print("  7 = governance-slide")
    print("  8 = text-slide")
    print("  9 = image-slide")
    print(" 10 = section-slide")

if __name__ == "__main__":
    main()
