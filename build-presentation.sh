#!/bin/bash
# Build a PowerPoint presentation from markdown using Python generator
# This is the main script - takes paths as parameters

set -e

# Usage check
if [ $# -lt 1 ]; then
    echo "Usage: $0 <markdown-file> [output-dir] [config-yaml]"
    echo ""
    echo "Arguments:"
    echo "  markdown-file - Path to markdown presentation source"
    echo "  output-dir    - Directory for output (default: same as markdown)"
    echo "  config-yaml   - Config file (default: concept_pack/template-config-v4.yaml)"
    echo ""
    echo "Example:"
    echo "  $0 ../example_concept_pack/example-concept-pack.md \\"
    echo "     ../example_concept_pack \\"
    echo "     ../example_concept_pack/presentation-config.yaml"
    echo ""
    echo "Output:"
    echo "  <output-dir>/<basename>.pptx"
    exit 1
fi

MARKDOWN_FILE="$1"
OUTPUT_DIR="${2:-$(dirname "$MARKDOWN_FILE")}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${3:-$SCRIPT_DIR/template-config-v4.yaml}"

# Resolve to absolute paths
MARKDOWN_FILE=$(cd "$(dirname "$MARKDOWN_FILE")" && pwd)/$(basename "$MARKDOWN_FILE")
OUTPUT_DIR=$(cd "$OUTPUT_DIR" && pwd)

BASENAME=$(basename "$MARKDOWN_FILE" .md)
OUTPUT_FILE="$OUTPUT_DIR/$BASENAME.pptx"

echo "📊 Building Presentation: $BASENAME"
echo "=========================================="
echo ""
echo "Input:  $MARKDOWN_FILE"
echo "Config: $CONFIG_FILE"
echo "Output: $OUTPUT_FILE"
echo ""

# Check if config exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Config file not found: $CONFIG_FILE"
    exit 1
fi

# Generate PowerPoint using Python script
# Change to markdown's directory so relative paths (like image:: output/file.png) work
echo "🔨 Generating PowerPoint..."
cd "$(dirname "$MARKDOWN_FILE")"
python3 "$SCRIPT_DIR/generate-concept-pack-v4-dynamic-fixed.py" \
  "$MARKDOWN_FILE" \
  "$OUTPUT_FILE" \
  "$CONFIG_FILE"

if [ -f "$OUTPUT_FILE" ]; then
    echo ""
    echo "✅ Done!"
    echo ""
    echo "Generated file:"
    echo "  📊 $OUTPUT_FILE"
else
    echo ""
    echo "❌ PowerPoint generation failed"
    exit 1
fi
