# Markdown Support in Presentations

The PowerPoint generator supports markdown formatting in `text::` blocks.

## Supported Markdown

### Headers
```markdown
# Level 1 Header
## Level 2 Header
### Level 3 Header
```

Headers are rendered **bold** in the presentation.

### Bold Text
```markdown
This is **bold text**
```

### Italic Text
```markdown
This is *italic text*
```

### Bullet Lists
```markdown
- First level bullet
- Another first level
  - Second level bullet
  - Another second level
```

Supports two levels of indentation.

## Example Content Slide

```markdown
# Key Components
slide-type:: content-slide
title:: Architecture Layers
category:: Technical

text::
## Presentation Layer
- Web UI for browser access
- Mobile App for iOS/Android
- API Gateway for integrations

## Business Logic
- Order Service for transaction processing
- User Service for account management
- Payment Service for financial operations

## Data Layer
- Database for persistent storage
- Cache for performance
- Object Storage for files
::end
```

## How It Works

When you use `text::` and `::end` to define content, the system:

1. **Detects markdown patterns**:
   - `#`, `##`, `###` at start of line → Headers (bold)
   - `**text**` → Bold
   - `*text*` → Italic
   - `- item` → Bullet list (level 0)
   - `  - item` → Bullet list (level 1, indented)

2. **Converts to PowerPoint formatting**:
   - Headers → Bold runs
   - Bold → Bold font
   - Italic → Italic font
   - Bullets → PowerPoint bullet formatting

3. **Preserves template styling**:
   - Font size from template
   - Font family from template
   - Color from template

## Combining Markdown

You can combine markdown styles:

```markdown
text::
## This is a **bold** header with *italic* text

- Regular bullet with **bold** and *italic* text
- Another bullet

Normal paragraph with **bold** words and *italic* words.
::end
```

## What's NOT Supported

The following markdown features are **not** supported:

❌ Links: `[text](url)`
❌ Images: `![alt](image.png)` (use `image::` field instead)
❌ Code blocks: ` ```code``` `
❌ Inline code: `` `code` ``
❌ Blockquotes: `> quote`
❌ Tables
❌ Horizontal rules: `---`
❌ Strikethrough: `~~text~~`

For these features, use PowerPoint's native formatting or add them manually.

## Tips

✅ **DO**: Use headers to organize sections
✅ **DO**: Use bullets for lists
✅ **DO**: Use **bold** for emphasis
✅ **DO**: Keep it simple - basic markdown works best

❌ **DON'T**: Use complex nested structures
❌ **DON'T**: Expect full markdown spec support
❌ **DON'T**: Mix too many styles in one line

## Troubleshooting

**Headers appear with `##` prefix:**
- Make sure you're using the updated generate-concept-pack script
- Check that headers are at the start of the line (no leading spaces)

**Bullets not formatting:**
- Check for exact syntax: `- ` (dash-space)
- For second level: `  - ` (two-spaces-dash-space)

**Bold/italic not working:**
- Check for matching delimiters: `**text**` and `*text*`
- No spaces between delimiters and text: `** text **` won't work

**Text appears blank:**
- Check you have `text::` and `::end` properly surrounding content
- Make sure there's content between them
