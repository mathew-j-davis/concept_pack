#!/usr/bin/env python3
"""
Generate PowerPoint concept pack from markdown content - v4 Dynamic (Fixed)

Builds presentations dynamically by cloning and reordering template slides.

Usage:
    python3 generate-concept-pack-v4-dynamic-fixed.py content.md output.pptx [config.yaml]
"""

import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE_TYPE
import yaml

# Import our markdown parser
from markdown_parser import parse_markdown_document

def load_template_config(config_file):
    """Load template configuration."""
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def hex_to_rgb(hex_color):
    """Convert hex color string to RGBColor."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        return RGBColor(
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        )
    return None

def clone_slide(prs, source_index):
    """
    Clone a slide within the same presentation.
    Returns the index of the new slide.
    """
    from pptx.oxml.xmlchemy import serialize_for_reading
    from copy import deepcopy
    import io

    source = prs.slides[source_index]

    # Get the slide's layout
    slide_layout = source.slide_layout

    # Create new slide with same layout
    new_slide = prs.slides.add_slide(slide_layout)

    # Remove all shapes from new slide (it starts with layout defaults)
    for shape in list(new_slide.shapes):
        sp = shape.element
        sp.getparent().remove(sp)

    # Copy all shapes from source
    for shape in source.shapes:
        el = shape.element
        newel = deepcopy(el)
        new_slide.shapes._spTree.append(newel)

    return len(prs.slides) - 1

# Import all the processing functions from v4
def find_shape_with_text(slide, text_to_find, partial=True):
    """Find a shape containing specific text."""
    def check_shape(shape):
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            for sub_shape in shape.shapes:
                result = check_shape(sub_shape)
                if result:
                    return result
        elif hasattr(shape, 'text'):
            if partial:
                if text_to_find in shape.text:
                    return shape
            else:
                if shape.text.strip() == text_to_find.strip():
                    return shape
        return None

    for shape in slide.shapes:
        result = check_shape(shape)
        if result:
            return result
    return None

def apply_markdown_formatting(text_frame, text_content):
    """
    Apply markdown formatting to text frame.
    Supports: **bold**, *italic*, and bullet lists (- item)
    """
    import re

    # Capture the font size from the first paragraph before clearing
    template_font_size = None
    template_font_name = None
    if text_frame.paragraphs and text_frame.paragraphs[0].runs:
        first_run = text_frame.paragraphs[0].runs[0]
        template_font_size = first_run.font.size
        template_font_name = first_run.font.name

    # Clear existing content
    for paragraph in list(text_frame.paragraphs[1:]):
        p_elem = paragraph._element
        p_elem.getparent().remove(p_elem)

    # Split into lines
    lines = text_content.split('\n')

    for line_idx, line in enumerate(lines):
        # Get or create paragraph
        if line_idx == 0:
            p = text_frame.paragraphs[0]
        else:
            p = text_frame.add_paragraph()

        # Check if it's a markdown header
        is_header = False
        header_level = 0
        if line.strip().startswith('## '):
            is_header = True
            header_level = 2
            line = line.strip()[3:]  # Remove "## "
        elif line.strip().startswith('### '):
            is_header = True
            header_level = 3
            line = line.strip()[4:]  # Remove "### "
        elif line.strip().startswith('# '):
            is_header = True
            header_level = 1
            line = line.strip()[2:]  # Remove "# "

        # Check if it's a bullet point
        is_bullet = False
        bullet_level = None

        if line.strip().startswith('- '):
            is_bullet = True
            bullet_level = 0
            line = line.strip()[2:]  # Remove "- "
        elif line.strip().startswith('  - '):
            is_bullet = True
            bullet_level = 1
            line = line.strip()[2:]  # Remove "  - "

        # Parse markdown formatting in line
        # Pattern: **bold** and *italic*
        segments = []

        # Combined pattern for **bold** and *italic*
        combined = r'(\*\*(.+?)\*\*)|(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)'

        last_end = 0
        for match in re.finditer(combined, line):
            # Add text before match
            if match.start() > last_end:
                segments.append({'text': line[last_end:match.start()], 'bold': False, 'italic': False})

            # Add formatted text
            if match.group(1):  # **bold**
                segments.append({'text': match.group(2), 'bold': True, 'italic': False})
            elif match.group(3):  # *italic*
                segments.append({'text': match.group(3), 'bold': False, 'italic': True})

            last_end = match.end()

        # Add remaining text
        if last_end < len(line):
            segments.append({'text': line[last_end:], 'bold': False, 'italic': False})

        # If no segments, just add the line as-is
        if not segments:
            segments = [{'text': line, 'bold': False, 'italic': False}]

        # Apply formatting to runs
        for seg_idx, segment in enumerate(segments):
            if seg_idx == 0:
                run = p.runs[0] if p.runs else p.add_run()
            else:
                run = p.add_run()

            run.text = segment['text']

            # Apply template font size to maintain consistency
            if template_font_size:
                run.font.size = template_font_size
            if template_font_name:
                run.font.name = template_font_name

            # Apply header formatting (bold, potentially larger)
            if is_header:
                run.font.bold = True
                # Optionally increase font size for headers
                # if template_font_size and header_level <= 2:
                #     run.font.size = int(template_font_size * 1.1)

            # Apply markdown formatting
            if segment['bold']:
                run.font.bold = True
            if segment['italic']:
                run.font.italic = True

        # Set bullet level AFTER creating runs
        # For bullet lines, set the level
        # For non-bullet lines, explicitly clear bullet formatting
        if is_bullet:
            p.level = bullet_level
        else:
            # Clear bullet formatting for non-bullet paragraphs
            # New paragraphs inherit template's bullet settings
            # So we need to explicitly disable bullets
            try:
                # Access the paragraph properties
                pPr = p._element.get_or_add_pPr()
                # Remove bullet formatting by clearing buNone, buChar, buAutoNum
                for child in list(pPr):
                    if child.tag.endswith('}buNone') or child.tag.endswith('}buChar') or child.tag.endswith('}buAutoNum'):
                        pPr.remove(child)
                # Add buNone to explicitly disable bullets
                from lxml import etree
                buNone = etree.SubElement(pPr, '{http://schemas.openxmlformats.org/drawingml/2006/main}buNone')
            except:
                # If this fails, just leave it
                pass

def replace_text_in_shape(shape, old_text, new_text):
    """Replace text in a shape, handling multi-run text."""
    if not hasattr(shape, 'text_frame'):
        return False

    text_frame = shape.text_frame
    replaced = False
    patterns = [f'<{old_text}>', f'‹{old_text}›']

    for paragraph in text_frame.paragraphs:
        full_text = ''.join(run.text for run in paragraph.runs)
        new_full_text = full_text

        for pattern in patterns:
            if pattern in new_full_text:
                new_full_text = new_full_text.replace(pattern, str(new_text))
                replaced = True

        if new_full_text != full_text:
            # Check if this looks like markdown content (has ** or * or -)
            has_markdown = '**' in new_full_text or '*' in new_full_text or '\n- ' in new_full_text

            if has_markdown:
                # Apply markdown formatting
                apply_markdown_formatting(text_frame, new_full_text)
            else:
                # Simple text replacement
                for run in paragraph.runs[1:]:
                    run.text = ''
                if paragraph.runs:
                    paragraph.runs[0].text = new_full_text

    return replaced

def replace_text_in_slide(slide, placeholder, value):
    """Replace text in all shapes in slide."""
    replaced = False

    def process_shape(shape):
        nonlocal replaced
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            for sub_shape in shape.shapes:
                if process_shape(sub_shape):
                    replaced = True
        else:
            if replace_text_in_shape(shape, placeholder, value):
                replaced = True
        return replaced

    for shape in slide.shapes:
        process_shape(shape)

    return replaced

def apply_fill_to_shape(shape, fill_color, text_color=None):
    """Apply fill and text color to a shape."""
    if fill_color:
        rgb = hex_to_rgb(fill_color)
        if rgb:
            shape.fill.solid()
            shape.fill.fore_color.rgb = rgb

    if text_color and hasattr(shape, 'text_frame'):
        rgb = hex_to_rgb(text_color)
        if rgb:
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.font.color.rgb = rgb

def color_top_bar_for_field(slide, placeholder, color):
    """Find the shape with placeholder and color the shape before it (top bar)."""
    def find_and_color_in_group(group_shapes):
        for idx, shape in enumerate(group_shapes):
            if hasattr(shape, 'text'):
                if f'<{placeholder}>' in shape.text or f'‹{placeholder}›' in shape.text:
                    if idx > 0:
                        top_bar = group_shapes[idx - 1]
                        rgb = hex_to_rgb(color)
                        if rgb:
                            top_bar.fill.solid()
                            top_bar.fill.fore_color.rgb = rgb
                            return True
        return False

    for shape in slide.shapes:
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            if find_and_color_in_group(shape.shapes):
                return True
    return False

def populate_table(slide, table_data, column_styling=None):
    """Populate a table on the slide with data."""
    table_shape = None
    for shape in slide.shapes:
        if shape.has_table:
            table_shape = shape
            break

    if not table_shape:
        return False

    table = table_shape.table
    headers = table_data.get('headers', [])
    rows_data = table_data.get('rows', [])

    header_map = {h: i for i, h in enumerate(headers)}

    row_idx = 1

    for row_data in rows_data:
        if row_idx < len(table.rows):
            row = table.rows[row_idx]
        else:
            from copy import deepcopy
            tr = deepcopy(table.rows[1]._tr)
            table._tbl.append(tr)
            row = table.rows[row_idx]

        for col_idx, cell_value in enumerate(row_data):
            if col_idx < len(row.cells):
                cell = row.cells[col_idx]
                cell.text = str(cell_value)

                if column_styling:
                    for col_name, col_styles in column_styling.items():
                        if col_name in header_map and header_map[col_name] == col_idx:
                            if 'style_by_value' in col_styles:
                                value_styles = col_styles['style_by_value']
                                if cell_value in value_styles:
                                    cell_style = value_styles[cell_value]

                                    if 'fill' in cell_style:
                                        rgb = hex_to_rgb(cell_style['fill'])
                                        if rgb:
                                            cell.fill.solid()
                                            cell.fill.fore_color.rgb = rgb

                                    if 'text_color' in cell_style:
                                        rgb = hex_to_rgb(cell_style['text_color'])
                                        if rgb and cell.text_frame:
                                            for paragraph in cell.text_frame.paragraphs:
                                                for run in paragraph.runs:
                                                    run.font.color.rgb = rgb

                if cell.text_frame:
                    for paragraph in cell.text_frame.paragraphs:
                        for run in paragraph.runs:
                            run.font.size = Pt(9)

        row_idx += 1

    while len(table.rows) > row_idx:
        try:
            table._tbl.remove(table.rows[-1]._tr)
        except:
            break

    return True

def generate_table_key(slide, table_data, column_styling, section_title):
    """
    Generate a dynamic key at the bottom of the slide based on values in the data.
    Removes any existing key shapes first.
    """
    from pptx.util import Inches, Pt
    from pptx.enum.shapes import MSO_SHAPE

    if not column_styling:
        return False

    # First, remove existing key shapes (shapes 5-10 in template)
    # We'll identify them by position (bottom of slide) and type
    shapes_to_remove = []
    for shape in slide.shapes:
        # Key shapes are at the bottom (top > 4.5 inches)
        if hasattr(shape, 'top') and shape.top > Inches(4.5):
            # Remove text boxes and rectangles at bottom
            if shape.shape_type in [MSO_SHAPE_TYPE.TEXT_BOX, MSO_SHAPE_TYPE.AUTO_SHAPE]:
                shapes_to_remove.append(shape)

    # Remove shapes (in reverse to avoid index issues)
    for shape in reversed(shapes_to_remove):
        sp = shape.element
        sp.getparent().remove(sp)

    # Collect unique values from the data
    headers = table_data.get('headers', [])
    rows_data = table_data.get('rows', [])

    # Find which columns are styled
    styled_values = {}  # {value: style_dict}

    for col_name, col_styles in column_styling.items():
        if col_name in headers and 'style_by_value' in col_styles:
            col_idx = headers.index(col_name)
            value_styles = col_styles['style_by_value']

            # Collect values that actually appear in the data
            for row in rows_data:
                if col_idx < len(row):
                    value = row[col_idx]
                    if value in value_styles:
                        styled_values[value] = value_styles[value]

    if not styled_values:
        return False

    # Generate key items
    # Position: start at left margin, bottom of slide
    start_left = Inches(0.8)
    start_top = Inches(5.0)
    box_size = Inches(0.15)
    spacing = Inches(2.5)

    for idx, (value, style) in enumerate(styled_values.items()):
        left_pos = start_left + (idx * spacing)

        # Add colored box
        box = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            left_pos,
            start_top,
            box_size,
            box_size
        )

        # Apply fill color
        if 'fill' in style:
            rgb = hex_to_rgb(style['fill'])
            if rgb:
                box.fill.solid()
                box.fill.fore_color.rgb = rgb

        # Remove border
        box.line.fill.background()

        # Add text label next to box
        text_left = left_pos + box_size + Inches(0.1)
        text_box = slide.shapes.add_textbox(
            text_left,
            start_top - Inches(0.02),  # Slight adjustment for alignment
            Inches(2.0),
            Inches(0.3)
        )

        text_frame = text_box.text_frame
        text_frame.text = value

        # Style the text
        for paragraph in text_frame.paragraphs:
            paragraph.font.size = Pt(10)
            paragraph.font.name = 'Calibri'

    return True

def insert_image_into_slide(slide, image_path, replace_placeholder=True, max_width_inches=None, max_height_inches=None):
    """
    Insert or replace image in slide.

    Args:
        slide: PowerPoint slide object
        image_path: Path to image file
        replace_placeholder: If True, finds and replaces existing picture shape
        max_width_inches: Optional maximum width in inches (overrides defaults)
        max_height_inches: Optional maximum height in inches (overrides defaults)

    Returns:
        True if successful, False otherwise
    """
    from pptx.util import Inches

    if not Path(image_path).exists():
        print(f"    ⚠ Image not found: {image_path}")
        return False

    if replace_placeholder:
        # Find existing picture shape
        picture_shape = None
        for shape in slide.shapes:
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                picture_shape = shape
                break

        if picture_shape:
            # Get position and size of placeholder (save for centering)
            placeholder_left = picture_shape.left
            placeholder_top = picture_shape.top
            placeholder_width = picture_shape.width
            placeholder_height = picture_shape.height

            # Remove placeholder
            sp = picture_shape.element
            sp.getparent().remove(sp)

            # Add new image temporarily to get dimensions
            pic = slide.shapes.add_picture(image_path, placeholder_left, placeholder_top)

            # Get image aspect ratio
            img_width, img_height = pic.image.size
            aspect_ratio = img_width / img_height

            # Calculate final size based on what's specified
            if max_width_inches is not None and max_height_inches is not None:
                # Both dimensions specified - fit within both constraints
                max_width = Inches(max_width_inches)
                max_height = Inches(max_height_inches)
                if max_width / max_height > aspect_ratio:
                    pic.height = max_height
                    pic.width = int(max_height * aspect_ratio)
                else:
                    pic.width = max_width
                    pic.height = int(max_width / aspect_ratio)

            elif max_width_inches is not None:
                # Only width specified - scale proportionally from width
                pic.width = Inches(max_width_inches)
                pic.height = int(pic.width / aspect_ratio)

            elif max_height_inches is not None:
                # Only height specified - scale proportionally from height
                pic.height = Inches(max_height_inches)
                pic.width = int(pic.height * aspect_ratio)

            else:
                # No custom size - fit within placeholder bounds
                if placeholder_width / placeholder_height > aspect_ratio:
                    pic.height = placeholder_height
                    pic.width = int(placeholder_height * aspect_ratio)
                else:
                    pic.width = placeholder_width
                    pic.height = int(placeholder_width / aspect_ratio)

            # Center within original placeholder area
            pic.left = placeholder_left + (placeholder_width - pic.width) // 2
            pic.top = placeholder_top + (placeholder_height - pic.height) // 2

            return True
    else:
        # Add image at center of slide
        # Typical slide is 10 x 7.5 inches
        slide_width = Inches(10)
        slide_height = Inches(7.5)

        pic = slide.shapes.add_picture(image_path, 0, 0)

        # Get image dimensions and aspect ratio
        img_width, img_height = pic.image.size
        aspect_ratio = img_width / img_height

        # Scale based on what's specified
        if max_width_inches is not None and max_height_inches is not None:
            # Both dimensions specified - fit within both constraints
            max_width = Inches(max_width_inches)
            max_height = Inches(max_height_inches)
            if max_width / max_height > aspect_ratio:
                pic.height = max_height
                pic.width = int(max_height * aspect_ratio)
            else:
                pic.width = max_width
                pic.height = int(max_width / aspect_ratio)

        elif max_width_inches is not None:
            # Only width specified - scale proportionally from width
            pic.width = Inches(max_width_inches)
            pic.height = int(pic.width / aspect_ratio)

        elif max_height_inches is not None:
            # Only height specified - scale proportionally from height
            pic.height = Inches(max_height_inches)
            pic.width = int(pic.height * aspect_ratio)

        else:
            # No dimensions specified - use defaults and fit within both
            max_width = Inches(8)
            max_height = Inches(5.5)
            if max_width / max_height > aspect_ratio:
                pic.height = max_height
                pic.width = int(max_height * aspect_ratio)
            else:
                pic.width = max_width
                pic.height = int(max_width / aspect_ratio)

        # Center on slide
        pic.left = (slide_width - pic.width) // 2
        pic.top = (slide_height - pic.height) // 2 + Inches(0.5)  # Offset down slightly

        return True

    return False

def process_section(slide, section, config):
    """Generic processor for a section."""
    fields = section.get('fields', {})
    tables = section.get('tables', [])
    operations_performed = []

    # Check for image insertion
    if 'image' in fields and fields['image'].get('value'):
        image_path = fields['image']['value']

        # Check for optional size parameters
        max_width = None
        max_height = None
        if 'image-width' in fields and fields['image-width'].get('value'):
            try:
                max_width = float(fields['image-width']['value'])
            except (ValueError, TypeError):
                print(f"    ⚠ Invalid image-width: {fields['image-width']['value']}")

        if 'image-height' in fields and fields['image-height'].get('value'):
            try:
                max_height = float(fields['image-height']['value'])
            except (ValueError, TypeError):
                print(f"    ⚠ Invalid image-height: {fields['image-height']['value']}")

        if insert_image_into_slide(slide, image_path, max_width_inches=max_width, max_height_inches=max_height):
            size_note = ""
            if max_width or max_height:
                size_parts = []
                if max_width:
                    size_parts.append(f"width={max_width}\"")
                if max_height:
                    size_parts.append(f"height={max_height}\"")
                size_note = f" ({', '.join(size_parts)})"
            operations_performed.append(f"Inserted image: {Path(image_path).name}{size_note}")

    for field_name, field_data in fields.items():
        # Skip image-related fields (already handled above)
        if field_name in ['image', 'image-width', 'image-height']:
            continue

        value = field_data.get('value')

        if value:
            if 'topbar-color' in field_data:
                color = field_data['topbar-color']
                if color_top_bar_for_field(slide, field_name, color):
                    operations_performed.append(f"Styled top bar for {field_name}")

            if replace_text_in_slide(slide, field_name, value):
                operations_performed.append(f"Replaced {field_name}")

            if 'fill' in field_data or 'text-color' in field_data:
                fill = field_data.get('fill')
                text_color = field_data.get('text-color')

                shape = find_shape_with_text(slide, f'<{field_name}>')
                if not shape:
                    shape = find_shape_with_text(slide, f'‹{field_name}›')

                if shape:
                    apply_fill_to_shape(shape, fill, text_color)
                    operations_performed.append(f"Styled {field_name}")

    if tables:
        # Get table-style field if specified
        table_style_name = None
        if 'table-style' in fields:
            table_style_data = fields['table-style']
            if isinstance(table_style_data, dict):
                table_style_name = table_style_data.get('value')
            else:
                table_style_name = table_style_data

        # Look up styling from config
        table_styles_config = config.get('table_styles', {})
        column_styling = None

        if table_style_name and table_style_name in table_styles_config:
            column_styling = table_styles_config[table_style_name]

        if populate_table(slide, tables[0], column_styling):
            operations_performed.append(f"Populated table with {len(tables[0]['rows'])} rows")

            # Generate dynamic key based on values in data
            if column_styling and generate_table_key(slide, tables[0], column_styling, section.get('title', '')):
                operations_performed.append(f"Generated dynamic key")

    return operations_performed

def generate_presentation(content_file, config_file, output_file):
    """Main generation function - builds presentation by cloning and reordering slides."""
    print(f"📖 Reading configuration from {config_file}...")
    config = load_template_config(config_file)
    template_file = config.get('template', 'concept_template.pptx')
    slide_types = config.get('slide_types', {})

    print(f"📖 Reading content from {content_file}...")
    with open(content_file, 'r') as f:
        content = f.read()

    parsed = parse_markdown_document(content)
    frontmatter = parsed['frontmatter']
    sections = parsed['sections']

    print(f"   Found {len(sections)} sections\n")

    print(f"📋 Loading template from {template_file}...")
    prs = Presentation(template_file)
    print(f"   Template has {len(prs.slides)} slides\n")

    print(f"🔨 Building presentation dynamically...")

    # Track which slides to keep and in what order
    slides_to_build = []

    # Add title slide if frontmatter exists
    if frontmatter:
        title_slide_num = slide_types.get('title-slide', 1)
        slides_to_build.append(('title', title_slide_num - 1, frontmatter, None))

    # Add requested slides from sections
    for section in sections:
        section_title = section.get('title', 'Untitled')

        # Get slide-type from section fields
        fields = section.get('fields', {})

        # Check for slide-type field
        slide_type = None
        if 'slide-type' in fields:
            slide_type_data = fields['slide-type']
            if isinstance(slide_type_data, dict):
                slide_type = slide_type_data.get('value')
            else:
                slide_type = slide_type_data

        if not slide_type:
            print(f"  ⚠ Skipping section '{section_title}' - no slide-type field")
            continue

        slide_num = slide_types.get(slide_type)
        if not slide_num:
            print(f"  ⚠ Skipping section '{section_title}' - unknown slide-type '{slide_type}'")
            continue

        slides_to_build.append((section_title, slide_num - 1, None, section))

    # Now clone the needed slides
    new_slide_indices = []

    for idx, (title, template_idx, frontmatter_data, section_data) in enumerate(slides_to_build):
        if idx == 0:
            # First slide - just use the existing one
            new_slide_indices.append(template_idx)
            print(f"\n🔧 Slide {idx + 1}: {title} (using template slide {template_idx + 1})...")
        else:
            # Clone the template slide
            print(f"\n🔧 Slide {idx + 1}: {title} (cloning template slide {template_idx + 1})...")
            new_idx = clone_slide(prs, template_idx)
            new_slide_indices.append(new_idx)

    # Process each slide
    for idx, (title, template_idx, frontmatter_data, section_data) in enumerate(slides_to_build):
        slide = prs.slides[new_slide_indices[idx]]

        if frontmatter_data:
            # Process frontmatter
            for key, value in frontmatter_data.items():
                if replace_text_in_slide(slide, key, value):
                    print(f"  ✓ Set {key}: {value}")
        elif section_data:
            # Process section
            operations = process_section(slide, section_data, config)
            for op in operations:
                print(f"  ✓ {op}")

    # Delete unused slides (those not in new_slide_indices)
    # Sort in reverse to delete from end first
    all_indices = set(range(len(prs.slides)))
    to_delete = sorted(all_indices - set(new_slide_indices), reverse=True)

    for idx in to_delete:
        rId = prs.slides._sldIdLst[idx].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[idx]

    # Reorder slides if needed
    # (python-pptx slides are in order, cloned slides are added at end)
    # We need to reorder the XML
    final_order = new_slide_indices

    print(f"\n💾 Saving to {output_file}...")
    prs.save(output_file)
    print(f"✅ Done! Generated {output_file} with {len(slides_to_build)} slides")

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 generate-concept-pack-v4-dynamic-fixed.py <content.md> <output.pptx> [config.yaml]")
        sys.exit(1)

    content_file = sys.argv[1]
    output_file = sys.argv[2]
    config_file = sys.argv[3] if len(sys.argv) > 3 else 'template-config-v4.yaml'

    if not Path(content_file).exists():
        print(f"❌ Content file not found: {content_file}")
        sys.exit(1)

    if not Path(config_file).exists():
        print(f"❌ Config file not found: {config_file}")
        sys.exit(1)

    generate_presentation(content_file, config_file, output_file)

if __name__ == '__main__':
    main()
