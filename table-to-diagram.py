#!/usr/bin/env python3
"""
Hierarchical table-based diagram generator.

Tables contain rows, rows contain columns, columns contain either cells or nested tables.
No spans needed - just pure recursive nesting.
"""

import yaml
import sys
import random
from pathlib import Path

class TableDiagramGenerator:
    """
    Generates boxesandarrows YAML from hierarchical table structure.

    Structure:
        table:
          width: 1000  # or 'auto'
          height: 800  # or 'auto'
          spacing: 0.2
          rows:
            - name: row1
              height: 700  # or 'auto'
              columns:
                - name: col1
                  width: 200  # or 'auto'
                  table:  # Nested table
                    rows: [...]
                - name: col2
                  width: auto
                  cell:   # Terminal cell
                    label: "Content"
                    type: header  # Optional styling
    """

    def __init__(self, config_path=None, input_file_dir=None):
        """
        Load configuration from YAML file.

        Args:
            config_path: Explicit config file path (highest priority)
            input_file_dir: Directory of input YAML file (to search for diagram-config.yaml)
        """
        # Determine which config to load (priority order)
        if config_path is None:
            # Try project-specific config first
            if input_file_dir:
                project_config = Path(input_file_dir) / 'diagram-config.yaml'
                if project_config.exists():
                    config_path = project_config

            # Fall back to default config
            if config_path is None:
                script_dir = Path(__file__).parent
                config_path = script_dir / 'conceptual-arch-config.yaml'

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.colors = self.config['colors']
        self.default_spacing = self.config['layout']['item_spacing']

        # Typography settings
        self.typography = self.config.get('typography', {})
        self.font_size = self.typography.get('font_size', 18)
        self.font_weight = self.typography.get('font_weight', 500)
        self.font_family = self.typography.get('font_family', 'Arial, sans-serif')

        # Border settings
        self.border = self.config.get('border', {})
        self.stroke_width = self.border.get('stroke_width', 1)

        self.cell_counter = 0

        # Icon settings
        self.input_file_dir = input_file_dir
        self.icons = []
        if input_file_dir:
            # Try icons directory in input file directory first
            icons_dir = Path(input_file_dir) / 'icons'
            if icons_dir.exists():
                self.icons = sorted([str(f.relative_to(input_file_dir)) for f in icons_dir.glob('*.svg')])
            else:
                # Try parent directory (for cases like diagram-definitions/example.yaml using ../icons/)
                parent_icons_dir = Path(input_file_dir).parent / 'icons'
                if parent_icons_dir.exists():
                    self.icons = sorted([str(f.relative_to(Path(input_file_dir).parent)) for f in parent_icons_dir.glob('*.svg')])

    def get_cell_style(self, cell_type):
        """Get colors for a cell based on its type."""
        if cell_type in self.colors:
            return self.colors[cell_type]
        return self.colors['box']  # Default

    def resolve_style(self, table_style=None, row_style=None, col_style=None, cell_spec=None):
        """
        Resolve style with cascading priority: cell > column > row > table > default

        Args:
            table_style: Style name or dict from table level
            row_style: Style name or dict from row level
            col_style: Style name or dict from column level
            cell_spec: Cell specification dict (may contain style/inline properties)

        Returns:
            dict with color keys (edge, fill, text) and font keys (font_size, font_weight, font_family)
        """
        # Start with default style (colors from box style, fonts from global defaults)
        style = dict(self.colors['box'])  # Copy colors (and any fonts defined in box style)

        # Set font defaults if not already in box style
        if 'font_size' not in style:
            style['font_size'] = self.font_size
        if 'font_weight' not in style:
            style['font_weight'] = self.font_weight
        if 'font_family' not in style:
            style['font_family'] = self.font_family

        # Apply styles in cascade order (each can override previous)
        for level_style in [table_style, row_style, col_style]:
            if level_style:
                if isinstance(level_style, str):
                    # Named style - look up in config and update all properties
                    if level_style in self.colors:
                        style.update(self.colors[level_style])
                elif isinstance(level_style, dict):
                    # Inline style dict - update all properties present
                    style.update(level_style)

        # Apply cell-level overrides (highest priority)
        if cell_spec:
            # Check for style field (named style or inline dict)
            cell_style = cell_spec.get('style')
            if cell_style:
                if isinstance(cell_style, str) and cell_style in self.colors:
                    # Named style - update all properties
                    style.update(self.colors[cell_style])
                elif isinstance(cell_style, dict):
                    # Inline style dict - update all properties present
                    style.update(cell_style)

            # Direct inline fields (highest priority)
            for prop in ['edge', 'fill', 'text', 'font_size', 'font_weight', 'font_family']:
                if prop in cell_spec:
                    style[prop] = cell_spec[prop]

        return style

    def normalize_color(self, color):
        """Ensure color has # prefix, handling both formats."""
        if not color:
            return '#000000'
        color = str(color).strip()
        if color.startswith('#'):
            return color
        return f"#{color}"

    def get_random_icon(self):
        """Get a random icon path from the available icons.
        Returns path relative to where boxesandarrows will be run from.
        """
        if not self.icons:
            return None
        # Return path as-is from icon list (already relative to project root)
        return random.choice(self.icons)

    def create_cell_def(self, cell_name, label, style, **positioning):
        """
        Create a cell definition with standard styling properties.

        Args:
            cell_name: Unique cell identifier
            label: Cell text
            style: Resolved style dict with colors and font properties
            **positioning: Positioning kwargs (x, y, w, h, position_of, anchor, etc.)
                          Can also include svg_icon, icon_label for icon support

        Returns:
            Complete cell definition dict
        """
        # Extract icon and icon_label if provided
        svg_icon = positioning.pop('svg_icon', None)
        icon_label = positioning.pop('icon_label', None)

        cell_def = {
            'type': 'node',
            'name': cell_name,
            'label': label,
            'shape': 'rectangle',
            'edge_color': self.normalize_color(style['edge']),
            'fill_color': self.normalize_color(style['fill']),
            'textcolor': self.normalize_color(style['text']),
            'font_size': style.get('font_size', self.font_size),
            'font_weight': style.get('font_weight', self.font_weight),
            'font_family': style.get('font_family', self.font_family),
            'stroke_width': self.stroke_width
        }

        # Add icon if provided - use svg_icon property
        if svg_icon:
            # Check if this is a header style (has 'header' in style dict or style is 'header')
            is_header = (isinstance(style, dict) and style.get('font_weight') == 700) or \
                       (isinstance(style, str) and 'header' in style.lower())

            cell_def['svg_icon'] = svg_icon

            if is_header:
                # Header style: icon on left, text centered on node
                cell_def['svg_icon_w'] = 1.0  # Icon width in cm
                cell_def['svg_icon_h'] = 1.0  # Icon height in cm
                cell_def['svg_icon_anchor'] = 'w'  # Position at left center
                cell_def['svg_icon_x_offset'] = 0.3  # Small offset from left edge
                # Text remains centered (default behavior, no text_anchor or offset changes)
            else:
                # Regular style: icon at top, text below in bottom half
                cell_def['svg_icon_w'] = 1.2  # Icon width in cm
                cell_def['svg_icon_h'] = 1.2  # Icon height in cm
                cell_def['svg_icon_anchor'] = 'n'  # Position at top center
                cell_def['svg_icon_y_offset'] = 0.2  # Small offset from top

                # If icon_label is provided, use it with y_offset to position in bottom half
                if icon_label:
                    cell_def['label'] = icon_label
                    cell_def['label_y_offset'] = 30  # Push label down (in pixels) to bottom half of cell

        # Add positioning properties
        cell_def.update(positioning)
        return cell_def

    def create_background_node(self, name, style, **positioning):
        """
        Create a background node behind cells.

        Args:
            name: Unique node identifier
            style: Style dict or style name string
            **positioning: Positioning kwargs

        Returns:
            Background node definition dict
        """
        # Resolve style if it's a string
        if isinstance(style, str) and style in self.colors:
            bg_style = self.colors[style]
        elif isinstance(style, dict):
            bg_style = style
        else:
            bg_style = {'edge': '000000', 'fill': 'FFFFFF'}

        bg_node = {
            'type': 'node',
            'name': name,
            'label': '',
            'shape': 'rectangle',
            'edge_color': self.normalize_color(bg_style.get('edge', '000000')),
            'fill_color': self.normalize_color(bg_style.get('fill', 'FFFFFF')),
            'textcolor': self.normalize_color(bg_style.get('text', '000000')),
            'stroke_width': bg_style.get('stroke_width', self.stroke_width),
            'hide_label': True
        }
        bg_node.update(positioning)
        return bg_node

    def calculate_dimensions(self, rows, available_width, available_height, spacing, table_column_widths=None):
        """
        Calculate actual widths and heights for rows and columns.

        Args:
            table_column_widths: Optional list of column widths defined at table level

        Returns:
            (row_heights, col_widths_per_row)
        """
        # Ensure available dimensions are numeric
        if available_height == 'auto':
            available_height = 40.0  # Default
        if available_width == 'auto':
            available_width = 48.0  # Default

        # Calculate row heights
        fixed_height = sum(row.get('height', 0) for row in rows if isinstance(row.get('height'), (int, float)))
        num_auto_rows = sum(1 for row in rows if row.get('height', 'auto') == 'auto')

        total_spacing = (len(rows) - 1) * spacing if len(rows) > 1 else 0
        remaining_height = available_height - fixed_height - total_spacing
        auto_row_height = remaining_height / num_auto_rows if num_auto_rows > 0 else 0

        row_heights = []
        for row in rows:
            h = row.get('height', 'auto')
            if h == 'auto':
                row_heights.append(auto_row_height)
            else:
                row_heights.append(h)

        # Calculate column widths for each row
        col_widths_per_row = []
        for row in rows:
            columns = row.get('columns', [])

            # Check if any column in this row has explicit width
            has_explicit_widths = any('width' in col for col in columns)

            # Use table-level column widths if available and no explicit widths in row
            if table_column_widths and not has_explicit_widths and len(columns) == len(table_column_widths):
                # Need to resolve 'auto' values in table_column_widths
                fixed_width = sum(w for w in table_column_widths if isinstance(w, (int, float)))
                num_auto = sum(1 for w in table_column_widths if w == 'auto')

                if num_auto > 0:
                    col_spacing = (len(table_column_widths) - 1) * spacing if len(table_column_widths) > 1 else 0
                    remaining_width = available_width - fixed_width - col_spacing
                    auto_width = remaining_width / num_auto

                    resolved_widths = [auto_width if w == 'auto' else w for w in table_column_widths]
                    col_widths_per_row.append(resolved_widths)
                else:
                    # All widths are numeric
                    col_widths_per_row.append(list(table_column_widths))
            else:
                # Calculate widths from column specifications
                fixed_width = sum(col.get('width', 0) for col in columns if isinstance(col.get('width'), (int, float)))
                num_auto_cols = sum(1 for col in columns if col.get('width', 'auto') == 'auto')

                col_spacing = (len(columns) - 1) * spacing if len(columns) > 1 else 0
                remaining_width = available_width - fixed_width - col_spacing
                auto_col_width = remaining_width / num_auto_cols if num_auto_cols > 0 else 0

                widths = []
                for col in columns:
                    w = col.get('width', 'auto')
                    if w == 'auto':
                        widths.append(auto_col_width)
                    else:
                        widths.append(w)
                col_widths_per_row.append(widths)

        return row_heights, col_widths_per_row

    def process_table(self, table_spec, x, y, width, height, parent_cell=None, horizontal_from_parent=False, align_with=None, parent_spacing=None):
        """
        Recursively process a table and generate positioned nodes.

        Args:
            table_spec: Table specification dict
            x, y: Absolute position (or None for relative)
            width, height: Available dimensions
            parent_cell: Parent cell name for relative positioning
            horizontal_from_parent: If True, position first cell horizontally (.ne) from parent
            align_with: Optional cell name to align x coordinate with (uses x_of)
            parent_spacing: Spacing inherited from parent row/column

        Returns:
            (documents, first_cell_name, last_cell_name)
        """
        documents = []
        rows = table_spec.get('rows', [])
        # Use table spacing if specified, else inherit from parent, else use default
        spacing = table_spec.get('spacing', parent_spacing if parent_spacing is not None else self.default_spacing)

        # Extract table-level style
        table_style = table_spec.get('style')

        # Extract table-level column widths (optional)
        table_column_widths = table_spec.get('column_widths')

        # Calculate dimensions
        row_heights, col_widths_per_row = self.calculate_dimensions(rows, width, height, spacing, table_column_widths)

        # Track positioning
        current_y = y
        prev_row_first_cell = parent_cell
        prev_row_bottom_cell = parent_cell  # Track bottom cell of previous row for vertical positioning
        first_cell_in_table = None
        last_cell_in_table = None

        for row_idx, row in enumerate(rows):
            # Track where this row's documents start so we can insert background first
            row_docs_start_idx = len(documents)

            columns = row.get('columns', [])
            row_height = row_heights[row_idx]
            col_widths = col_widths_per_row[row_idx]

            # Extract row-level style
            row_style = row.get('style')

            # Row-level spacing override
            row_spacing = row.get('spacing', spacing)

            current_x = x
            prev_cell_in_row = None
            first_cell_in_row = None
            last_cell_in_row = None  # Track last cell for background node (rightmost)
            last_col_bottom_cell = None  # Track bottom cell of last column for background height
            first_col_last_cell = None  # Track last cell of first column for next row positioning
            cumulative_x_offset = 0  # Track cumulative x offset for columns with nested tables

            for col_idx, column in enumerate(columns):
                col_width = col_widths[col_idx]

                # Column-level spacing override
                col_spacing = column.get('spacing', row_spacing)

                # Check if column has a cell, cells_stack, or nested table
                if 'cells_stack' in column:
                    # Vertical stack of cells - process as a mini table with one column
                    cells = column['cells_stack']

                    # Create a mini table structure
                    # Inherit table and row styles, and column spacing
                    col_style = column.get('style')
                    mini_table = {
                        'style': col_style,  # Column style becomes table style for mini-table
                        'rows': []
                    }
                    # Pass column spacing to mini table if specified
                    if 'spacing' in column:
                        mini_table['spacing'] = column['spacing']
                    for cell_spec in cells:
                        # Cell style can override column style
                        cell_style = cell_spec.get('style') or row_style
                        mini_table['rows'].append({
                            'height': cell_spec.get('height', 'auto'),
                            'style': cell_style,
                            'columns': [{
                                'width': col_width,
                                'cell': cell_spec
                            }]
                        })

                    # Process as nested table
                    if col_idx == 0:
                        parent = prev_row_bottom_cell if prev_row_bottom_cell else parent_cell
                        nested_docs, nested_first, nested_last = self.process_table(
                            mini_table,
                            current_x if parent is None else None,
                            current_y if parent is None else None,
                            col_width,
                            row_height,
                            parent,
                            horizontal_from_parent=False,
                            align_with=None,
                            parent_spacing=col_spacing
                        )
                        cumulative_x_offset = row_spacing  # Horizontal gap between columns
                    else:
                        if cumulative_x_offset > 0 and first_cell_in_row:
                            nested_docs, nested_first, nested_last = self.process_table(
                                mini_table,
                                None,
                                None,
                                col_width,
                                row_height,
                                first_cell_in_row,
                                horizontal_from_parent=True,
                                align_with=None,
                                parent_spacing=col_spacing
                            )
                            if nested_docs and len(nested_docs) > 0:
                                nested_docs[0]['x_offset'] = cumulative_x_offset
                        else:
                            nested_docs, nested_first, nested_last = self.process_table(
                                mini_table,
                                None,
                                None,
                                col_width,
                                row_height,
                                prev_cell_in_row,
                                horizontal_from_parent=True,
                                align_with=None,
                                parent_spacing=col_spacing
                            )
                        # Only update cumulative offset if width is numeric (not 'auto')
                        if isinstance(col_width, (int, float)):
                            cumulative_x_offset += col_width + row_spacing  # Horizontal: use row-level spacing

                    # Add column background if specified (before the cells so it renders behind)
                    col_bg_inserted = False
                    if 'background' in column and nested_first:
                        col_bg_name = f"{nested_first}_col_bg"
                        col_bg_style = column['background']
                        col_bg_node = self.create_background_node(
                            col_bg_name,
                            col_bg_style,
                            position_of=f'{nested_first}.nw',
                            anchor='nw',
                            w=col_width,
                            h=row_height,
                            x_offset=0,
                            y_offset=0
                        )
                        # Insert BEFORE the nested docs by inserting at current document position
                        # Then shift nested_docs positions by inserting the background into nested_docs at position 0
                        nested_docs.insert(0, col_bg_node)
                        col_bg_inserted = True

                    documents.extend(nested_docs)

                    if first_cell_in_table is None:
                        first_cell_in_table = nested_first
                    if first_cell_in_row is None:
                        first_cell_in_row = nested_first

                    prev_cell_in_row = nested_first
                    last_cell_in_table = nested_last
                    last_cell_in_row = nested_last

                    if col_idx == 0:
                        first_col_last_cell = nested_last
                    if col_idx == len(columns) - 1:
                        last_col_bottom_cell = nested_last

                elif 'cell' in column:
                    # Terminal cell
                    cell = column['cell']

                    # Extract column-level style
                    col_style = column.get('style')

                    # Resolve style with full cascade: table → row → column → cell
                    style = self.resolve_style(table_style, row_style, col_style, cell)

                    cell_name = cell.get('name', f"cell_{self.cell_counter}")
                    self.cell_counter += 1

                    # Get icon and icon_label from cell spec if provided
                    icon_path = None
                    icon_label_text = None
                    if 'icon' in cell:
                        # Icon paths need to start with ./ or / for boxesandarrows to recognize them as file paths
                        # Ensure the path starts with ./
                        raw_path = cell['icon']
                        if not raw_path.startswith(('./','../', '/', 'http')):
                            icon_path = f"./{raw_path}"
                        else:
                            icon_path = raw_path

                        # Check if icon_label is specified (if so, use it; otherwise use label)
                        icon_label_text = cell.get('icon_label', cell.get('label', ''))

                    # Positioning logic
                    if parent_cell is None and row_idx == 0 and col_idx == 0:
                        # First cell in entire diagram - absolute position
                        cell_def = self.create_cell_def(
                            cell_name,
                            cell.get('label', ''),
                            style,
                            anchor='nw',
                            x=current_x,
                            y=current_y,
                            w=col_width,
                            h=row_height,
                            svg_icon=icon_path,
                            icon_label=icon_label_text
                        )
                        # Add x_of if align_with is specified
                        if align_with and row_idx == 0 and col_idx == 0:
                            cell_def['x_of'] = align_with
                        documents.append(cell_def)
                        first_cell_in_table = cell_name
                        first_cell_in_row = cell_name
                    elif col_idx == 0:
                        # First cell in row - position below previous row OR horizontally from parent
                        ref = prev_row_bottom_cell if prev_row_bottom_cell else parent_cell

                        if row_idx == 0 and horizontal_from_parent and parent_cell:
                            # First row and should position horizontally from parent
                            # BUT if align_with is set, position vertically from align target, use x_of for x alignment
                            align_target = column.get('align_with') or align_with
                            if align_target:
                                # Position vertically from align target, use x_of for horizontal alignment
                                cell_def = self.create_cell_def(
                                    cell_name,
                                    cell.get('label', ''),
                                    style,
                                    position_of=f'{align_target}.sw',
                                    anchor='nw',
                                    y_offset=spacing,
                                    w=col_width,
                                    h=row_height,
                                    x_of=align_target,
                                    svg_icon=icon_path,
                                    icon_label=icon_label_text
                                )
                            else:
                                # Normal horizontal positioning
                                cell_def = self.create_cell_def(
                                    cell_name,
                                    cell.get('label', ''),
                                    style,
                                    position_of=f'{ref}.ne',
                                    anchor='nw',
                                    x_offset=spacing,
                                    w=col_width,
                                    h=row_height,
                                    svg_icon=icon_path,
                                    icon_label=icon_label_text
                                )
                            documents.append(cell_def)
                        else:
                            # Position below
                            cell_def = self.create_cell_def(
                                cell_name,
                                cell.get('label', ''),
                                style,
                                position_of=f'{ref}.sw',
                                anchor='nw',
                                y_offset=spacing,
                                w=col_width,
                                h=row_height,
                                svg_icon=icon_path,
                                icon_label=icon_label_text
                            )
                            # Check if column has align_with or if align_with parameter is set
                            if 'align_with' in column:
                                cell_def['x_of'] = column['align_with']
                            elif align_with:
                                cell_def['x_of'] = align_with
                            documents.append(cell_def)
                        if first_cell_in_table is None:
                            first_cell_in_table = cell_name
                        first_cell_in_row = cell_name
                    else:
                        # Cell to the right of previous
                        cell_def = self.create_cell_def(
                            cell_name,
                            cell.get('label', ''),
                            style,
                            position_of=f'{prev_cell_in_row}.ne',
                            anchor='nw',
                            x_offset=row_spacing,  # Horizontal: use row-level spacing
                            w=col_width,
                            h=row_height,
                            svg_icon=icon_path,
                            icon_label=icon_label_text
                        )
                        # Check if column has align_with or if align_with parameter is set
                        if 'align_with' in column:
                            cell_def['x_of'] = column['align_with']
                        elif align_with and row_idx == 0:
                            cell_def['x_of'] = align_with
                        documents.append(cell_def)

                    prev_cell_in_row = cell_name
                    last_cell_in_table = cell_name
                    last_cell_in_row = cell_name

                    # Track last cell of first column
                    if col_idx == 0:
                        first_col_last_cell = cell_name
                    if col_idx == len(columns) - 1:
                        last_col_bottom_cell = cell_name

                elif 'table' in column:
                    # Nested table - recurse
                    nested_table = column['table']
                    column_align_with = column.get('align_with')

                    # Determine parent cell for relative positioning
                    # For the first column in a row, position relative to previous row (vertical)
                    # For subsequent columns, position relative to previous column (horizontal)
                    if col_idx == 0:
                        parent = prev_row_bottom_cell if prev_row_bottom_cell else parent_cell
                        nested_docs, nested_first, nested_last = self.process_table(
                            nested_table,
                            current_x if parent is None else None,
                            current_y if parent is None else None,
                            col_width,
                            row_height,
                            parent,
                            horizontal_from_parent=False,  # Vertical positioning
                            align_with=column_align_with,
                            parent_spacing=col_spacing
                        )
                        # Start cumulative offset AFTER first column (don't include first column width)
                        cumulative_x_offset = row_spacing  # Horizontal gap between columns
                    else:
                        # Position relative to the previous column
                        # Use cumulative_x_offset to account for full column widths, not just first cells
                        if cumulative_x_offset > 0 and first_cell_in_row:
                            # Calculate where this column should start based on column widths
                            # We'll create a custom positioning that uses x_offset from the first cell in row
                            nested_docs, nested_first, nested_last = self.process_table(
                                nested_table,
                                None,
                                None,
                                col_width,
                                row_height,
                                first_cell_in_row,  # Position relative to first cell in row
                                horizontal_from_parent=True,  # Horizontal positioning
                                align_with=column_align_with,
                                parent_spacing=col_spacing
                            )
                            # Adjust the first nested cell to use the correct x_offset
                            if nested_docs and len(nested_docs) > 0:
                                nested_docs[0]['x_offset'] = cumulative_x_offset
                        else:
                            nested_docs, nested_first, nested_last = self.process_table(
                                nested_table,
                                None,
                                None,
                                col_width,
                                row_height,
                                prev_cell_in_row,  # Position relative to previous column
                                horizontal_from_parent=True,  # Horizontal positioning
                                align_with=column_align_with,
                                parent_spacing=col_spacing
                            )
                        # Only update cumulative offset if width is numeric (not 'auto')
                        if isinstance(col_width, (int, float)):
                            cumulative_x_offset += col_width + row_spacing  # Horizontal: use row-level spacing

                    documents.extend(nested_docs)

                    if first_cell_in_table is None:
                        first_cell_in_table = nested_first
                    if first_cell_in_row is None:
                        first_cell_in_row = nested_first

                    # Track the first cell of this nested table for the next column
                    prev_cell_in_row = nested_first
                    last_cell_in_table = nested_last
                    last_cell_in_row = nested_last

                    # Track last cell of first column for next row positioning
                    if col_idx == 0:
                        first_col_last_cell = nested_last
                    if col_idx == len(columns) - 1:
                        last_col_bottom_cell = nested_last

                if current_x is not None:
                    current_x += col_width + col_spacing

            # Add background node if specified (insert at start of row docs so it renders behind)
            if 'background' in row and first_cell_in_row and last_cell_in_row:
                bg_name = f"{first_cell_in_row}_row_bg"
                bg_style = row['background']

                # Calculate explicit width and height
                # Width = sum of all column widths + spacing between them
                bg_width = sum(col_widths) + (len(col_widths) - 1) * row_spacing if len(col_widths) > 1 else sum(col_widths)
                # Height = row height
                bg_height = row_height

                bg_node = self.create_background_node(
                    bg_name,
                    bg_style,
                    position_of=f'{first_cell_in_row}.nw',
                    anchor='nw',
                    w=bg_width,
                    h=bg_height,
                    x_offset=0,  # No horizontal offset
                    y_offset=0   # No vertical offset
                )
                # Insert at the beginning of this row's documents (so it renders first/behind)
                documents.insert(row_docs_start_idx, bg_node)

            if first_cell_in_row:
                prev_row_first_cell = first_cell_in_row
            # Update bottom cell tracker for next row
            if first_col_last_cell:
                prev_row_bottom_cell = first_col_last_cell
            if current_y is not None:
                current_y += row_height + row_spacing

        return documents, first_cell_in_table, last_cell_in_table

    def generate_yaml_from_table(self, table_spec):
        """
        Generate boxesandarrows YAML from table specification.

        Args:
            table_spec: Root table dict

        Returns:
            List of YAML documents (dicts)
        """
        # Get root dimensions
        width = table_spec.get('width', 48.0)
        height = table_spec.get('height', 40.0)
        start_x = table_spec.get('start_x', 2.0)
        start_y = table_spec.get('start_y', 2.0)

        # Convert 'auto' to defaults
        if width == 'auto':
            width = 48.0
        if height == 'auto':
            height = 40.0

        # Process the table recursively
        documents, _, _ = self.process_table(table_spec, start_x, start_y, width, height, parent_cell=None, horizontal_from_parent=False, align_with=None)

        # === PAGE CONFIGURATION ===
        documents.append({
            'type': 'page',
            'background': 'white',
            'scale': {
                'position': {'x': 60, 'y': 60},
                'size': {'w': 60, 'h': 60}
            },
            'margin': {'w': 1, 'h': 1}
        })

        # === BASE STYLE ===
        documents.append({
            'type': 'style',
            'name': 'base',
            'node': {
                'object': {
                    'svg': {
                        'stroke-width': 1,
                        'rx': 3,
                        'ry': 3
                    }
                },
                'text': {
                    'svg': {
                        'font-family': 'Arial, sans-serif',
                        'font-size': '20px',
                        'font-weight': '500',
                        'text-anchor': 'middle',
                        'dominant-baseline': 'middle'
                    }
                }
            }
        })

        return documents

    def save_yaml(self, documents, output_path):
        """Save YAML documents to file."""
        with open(output_path, 'w') as f:
            for doc in documents:
                f.write('---\n')
                yaml.dump(doc, f, default_flow_style=False, sort_keys=False)
                f.write('\n')

def load_table_spec(input_path):
    """Load table specification from YAML file."""
    with open(input_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    if len(sys.argv) < 3:
        print("Usage: python table-to-diagram.py <table.yaml> <output.yaml>")
        print()
        print("Example table.yaml:")
        print("""
table:
  width: 48.0
  height: 40.0
  spacing: 0.2
  start_x: 2.0
  start_y: 2.0
  rows:
    - name: main
      height: 700
      columns:
        - name: col1
          width: 200
          table:
            rows:
              - height: auto
                columns:
                  - cell:
                      label: "Nested cell"
        - name: col2
          width: auto
          cell:
            label: "Simple cell"
            type: header
        """)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    print(f"📖 Reading table specification from {input_file}...")
    spec = load_table_spec(input_file)

    # Get input file's directory to search for diagram-config.yaml
    input_dir = Path(input_file).parent

    print(f"🔨 Generating diagram YAML from table...")
    generator = TableDiagramGenerator(input_file_dir=input_dir)
    documents = generator.generate_yaml_from_table(spec['table'])

    print(f"💾 Saving to {output_file}...")
    generator.save_yaml(documents, output_file)

    print(f"✅ Done! Generated {output_file}")
    print(f"\nTo generate SVG:")
    print(f"  cd ../boxesandarrows")
    print(f"  node src/index.js -y {output_file} -r svg -o output/diagram")

if __name__ == '__main__':
    main()
