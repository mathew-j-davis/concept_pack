"""
Markdown parser for concept pack content files.

Parses markdown documents with:
- YAML frontmatter
- Sections divided by ---
- Inline fields (name:: value)
- Markdown tables
- Text blocks
"""

import re
import yaml

def parse_frontmatter(content):
    """Extract YAML frontmatter from markdown."""
    # Match --- at start, content, then ---
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(pattern, content, re.DOTALL)

    if match:
        frontmatter_text = match.group(1)
        body = content[match.end():]
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            return frontmatter, body
        except:
            return {}, content

    return {}, content

def extract_first_header(text):
    """Extract the first markdown header (# Title)."""
    lines = text.strip().split('\n')
    for line in lines:
        if line.startswith('#'):
            # Remove # symbols and whitespace
            return line.lstrip('#').strip()
    return None

def parse_inline_fields(text):
    """
    Parse inline fields with :: syntax.
    Supports both single-line and multi-line blocks:

    Single-line:
        roadmap-fit:: On-roadmap
        roadmap-fit-topbar-color:: 00B050

    Multi-line block:
        opportunity-recommendation::
        The recommendation is to proceed with design...
        This approach leverages...
        ::end

    Returns:
    {
        'roadmap-fit': {
            'value': 'On-roadmap',
            'topbar-color': '00B050'
        },
        'opportunity-recommendation': {
            'value': 'The recommendation is...'
        }
    }
    """
    fields = {}
    lines = text.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        if '::' in line and not line.strip() == '::end':
            parts = line.split('::', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()

                # Check if this is a multi-line block (value is empty or just whitespace)
                if not value:
                    # Multi-line block - read until ::end
                    block_lines = []
                    i += 1
                    while i < len(lines):
                        if lines[i].strip() == '::end':
                            break
                        block_lines.append(lines[i])
                        i += 1

                    value = '\n'.join(block_lines).strip()

                    # Store as base field
                    if key not in fields:
                        fields[key] = {}
                    fields[key]['value'] = value

                else:
                    # Single-line field
                    # Parse key into base and suffix
                    if '-' in key:
                        # Strategy: known style suffixes
                        style_suffixes = ['topbar-color', 'fill', 'text-color', 'border', 'border-width']

                        base_name = key
                        suffix = None

                        for style_suffix in style_suffixes:
                            if key.endswith(f'-{style_suffix}'):
                                base_name = key[:-len(style_suffix)-1]
                                suffix = style_suffix
                                break

                        if suffix:
                            # It's a style property
                            if base_name not in fields:
                                fields[base_name] = {}
                            fields[base_name][suffix] = value
                        else:
                            # It's a base field
                            if key not in fields:
                                fields[key] = {}
                            fields[key]['value'] = value
                    else:
                        # Simple key with no dashes
                        if key not in fields:
                            fields[key] = {}
                        fields[key]['value'] = value

        i += 1

    return fields

def parse_markdown_table(text):
    """
    Parse markdown table into list of rows.

    Returns:
    {
        'headers': ['Column1', 'Column2', ...],
        'rows': [
            ['cell1', 'cell2', ...],
            ['cell1', 'cell2', ...],
        ]
    }
    """
    lines = text.split('\n')

    headers = None
    rows = []

    for line in lines:
        line = line.strip()
        if not line or not '|' in line:
            continue

        # Skip separator line (|---|---|---|)
        # Pattern: starts with |, contains only dashes/colons/spaces/pipes, ends with |
        if re.match(r'^\|[\s\-:|]+$', line) and '--' in line:
            continue

        # Parse cells
        cells = [c.strip() for c in line.split('|')]
        # Remove empty first/last if line starts/ends with |
        if cells and cells[0] == '':
            cells = cells[1:]
        if cells and cells[-1] == '':
            cells = cells[:-1]

        if not cells:
            continue

        if headers is None:
            headers = cells
        else:
            rows.append(cells)

    if headers:
        return {
            'headers': headers,
            'rows': rows
        }

    return None

def extract_tables(text):
    """Extract all markdown tables from text."""
    tables = []

    # Find table blocks (consecutive lines with |)
    lines = text.split('\n')
    current_table_lines = []

    for line in lines:
        if '|' in line:
            current_table_lines.append(line)
        else:
            if current_table_lines:
                # End of table, parse it
                table_text = '\n'.join(current_table_lines)
                table = parse_markdown_table(table_text)
                if table:
                    tables.append(table)
                current_table_lines = []

    # Handle table at end of text
    if current_table_lines:
        table_text = '\n'.join(current_table_lines)
        table = parse_markdown_table(table_text)
        if table:
            tables.append(table)

    return tables

def extract_text_blocks(text):
    """
    Extract text blocks excluding inline fields and tables.
    Returns text organized by subsection headers.
    """
    blocks = {}
    current_header = None
    current_text = []

    lines = text.split('\n')

    for line in lines:
        # Skip inline fields
        if '::' in line and not line.strip().startswith('#'):
            continue

        # Skip table lines
        if '|' in line:
            continue

        # Check for subsection header (## Header)
        if line.startswith('##'):
            # Save previous block
            if current_header and current_text:
                blocks[current_header] = '\n'.join(current_text).strip()

            current_header = line.lstrip('#').strip()
            current_text = []
        elif line.strip():
            # Add to current text
            current_text.append(line)

    # Save last block
    if current_header and current_text:
        blocks[current_header] = '\n'.join(current_text).strip()

    return blocks

def parse_section(section_text):
    """Parse a single section into structured data."""
    title = extract_first_header(section_text)
    fields = parse_inline_fields(section_text)
    tables = extract_tables(section_text)
    text_blocks = extract_text_blocks(section_text)

    return {
        'title': title,
        'fields': fields,
        'tables': tables,
        'text_blocks': text_blocks,
        'raw': section_text
    }

def parse_markdown_document(content):
    """
    Parse complete markdown document.

    Returns:
    {
        'frontmatter': {...},
        'sections': [
            {
                'title': 'Section Title',
                'fields': {...},
                'tables': [...],
                'text_blocks': {...}
            },
            ...
        ]
    }
    """
    # Extract frontmatter
    frontmatter, body = parse_frontmatter(content)

    # Split into sections by ---
    # Use regex to split on lines that are just ---
    section_texts = re.split(r'\n---+\n', body)

    sections = []
    for section_text in section_texts:
        section_text = section_text.strip()
        if not section_text:
            continue

        section = parse_section(section_text)
        sections.append(section)

    return {
        'frontmatter': frontmatter,
        'sections': sections
    }

# Test function
if __name__ == '__main__':
    test_content = """---
title: Test Document
author: Test Author
---

# Executive Summary

opportunity-name:: AI Gateway
opportunity-number:: OD-2024-089

roadmap-fit:: On-roadmap
roadmap-fit-topbar-color:: 00B050

This is some text that describes the opportunity.

---

# Technology Stack

| Capability | Technology | Status |
|------------|------------|--------|
| API Gateway | AWS API Gateway | Reuse |
| Model Access | AWS Bedrock | Reuse |

Status colors are defined in config.
"""

    result = parse_markdown_document(test_content)

    print("Frontmatter:")
    print(result['frontmatter'])
    print("\nSections:")
    for section in result['sections']:
        print(f"\n  Title: {section['title']}")
        print(f"  Fields: {section['fields']}")
        print(f"  Tables: {len(section['tables'])}")
        print(f"  Text blocks: {list(section['text_blocks'].keys())}")
