# Styling Guide - Hierarchical Style System

The table-to-diagram generator supports applying styles at multiple levels with cascading priority.

## Priority Order (Highest to Lowest)

1. **Inline cell colors** - Direct color fields on cell
2. **Cell style** - `style:` or `type:` field on cell
3. **Column style** - `style:` or `type:` field on column
4. **Row style** - `style:` or `type:` field on row
5. **Table style** - `style:` or `type:` field on table
6. **Default style** - From config (`colors.box`)

## Usage Examples

### 1. Named Styles

Define styles in `conceptual-arch-config.yaml`:

```yaml
colors:
  box:        # Default style
    edge: '1F6FA8'
    fill: 'E8F4F8'
    text: '000000'
  
  header:
    edge: '1F6FA8'
    fill: 'D6EAF8'
    text: '000000'
  
  important:
    edge: 'DC3545'
    fill: 'FFE6E9'
    text: '000000'
```

Use in diagram YAML:

```yaml
table:
  style: box          # Apply to entire table
  rows:
    - style: header   # Override for this row
      columns:
        - cell:
            label: "Title"
```

### 2. Inline Styles

Override colors directly (highest priority):

```yaml
cell:
  label: "Critical"
  edge: 'FF0000'      # Red border
  fill: 'FFCCCC'      # Light red fill
  text: '000000'      # Black text
```

### 3. Style Cascade Example

```yaml
table:
  style: box          # Default blue
  rows:
    # Header row
    - style: header   # Darker blue for entire row
      columns:
        - cell:
            label: "USERS"
            
    # Content row
    - columns:
        # Normal column (inherits table style)
        - cell:
            label: "Customer"
            
        # Important column
        - style: important   # Red border for all cells in column
          cell:
            label: "Critical Data"
            
        # Cell override
        - cell:
            label: "Special"
            style: highlight   # This cell only
            
        # Inline override
        - cell:
            label: "Custom"
            fill: 'FFFF00'     # Yellow fill (highest priority)
```

### 4. Styling cells_stack

```yaml
columns:
  - style: header          # Apply to all cells in stack
    cells_stack:
      - label: "USERS"     # Inherits header style
        height: 2.0
      - label: "Customers"  # Inherits header style
      - label: "Staff"
        style: important   # Override for this cell only
```

### 5. Nested Table Styles

```yaml
columns:
  - table:               # Nested table
      style: foundation  # Different style for nested content
      rows:
        - columns:
            - cell:
                label: "Layer 1"
```

## Style Fields

Three color fields can be styled:

- `edge` - Border color (hex without #)
- `fill` - Background color (hex without #)
- `text` - Text color (hex without #)

## Style Field

Use the `style:` field to apply named styles or inline style dicts:

```yaml
row:
  style: header    # Apply named style
  columns:
    - cell:
        style: box  # Apply named style
```

## Tips

1. **Define reusable styles** in config for consistency
2. **Use table/row styles** for large areas
3. **Use column styles** for vertical sections
4. **Use cell styles** for individual emphasis
5. **Use inline colors** for one-off customization
6. **Mix approaches** - cascade makes it flexible!

## Example: Status Colors

```yaml
# In config
colors:
  status_ok:
    edge: '28A745'
    fill: 'E6F9EC'
    text: '000000'
  
  status_warning:
    edge: 'FFC107'
    fill: 'FFF8E1'
    text: '000000'
  
  status_error:
    edge: 'DC3545'
    fill: 'FFE6E9'
    text: '000000'

# In diagram
table:
  rows:
    - columns:
        - cell:
            label: "Service A"
            style: status_ok
        - cell:
            label: "Service B"
            style: status_warning
        - cell:
            label: "Service C"
            style: status_error
```
