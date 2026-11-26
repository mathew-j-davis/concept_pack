#!/bin/bash
# Build a diagram from table YAML to SVG and PNG
# This is the main script - takes paths as parameters

set -e

# Usage check
if [ $# -lt 2 ]; then
    echo "Usage: $0 <table-yaml> <output-name> [project-dir]"
    echo ""
    echo "Arguments:"
    echo "  table-yaml   - Path to table-based architecture YAML"
    echo "  output-name  - Name for output files (without extension)"
    echo "  project-dir  - Project directory (for config and node_modules)"
    echo ""
    echo "Example:"
    echo "  $0 ../example_concept_pack/diagram-definitions/architecture.yaml \\"
    echo "     architecture \\"
    echo "     ../example_concept_pack"
    echo ""
    echo "Output:"
    echo "  <project-dir>/output/<output-name>.svg"
    echo "  <project-dir>/output/<output-name>.png"
    exit 1
fi

TABLE_YAML="$1"
OUTPUT_NAME="$2"
PROJECT_DIR="${3:-.}"

# Resolve to absolute paths
TABLE_YAML=$(cd "$(dirname "$TABLE_YAML")" && pwd)/$(basename "$TABLE_YAML")
PROJECT_DIR=$(cd "$PROJECT_DIR" && pwd)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🎨 Building Diagram: $OUTPUT_NAME"
echo "=========================================="
echo ""
echo "Input:   $TABLE_YAML"
echo "Output:  $PROJECT_DIR/output/$OUTPUT_NAME.{svg,png}"
echo ""

# Create output directory
mkdir -p "$PROJECT_DIR/output"

# Generate intermediate positioned YAML
POSITIONED_YAML="$PROJECT_DIR/output/${OUTPUT_NAME}-positioned.yaml"

# Step 1: Convert table to positioned boxes
echo "📋 Step 1: Converting table to positioned boxes..."
python3 "$SCRIPT_DIR/table-to-diagram.py" "$TABLE_YAML" "$POSITIONED_YAML"

# Step 2: Generate SVG
echo ""
echo "🖼️  Step 2: Generating SVG..."
node "$SCRIPT_DIR/../boxesandarrows/src/index.js" \
  -y "$POSITIONED_YAML" \
  -r svg \
  -o "$PROJECT_DIR/output/$OUTPUT_NAME"

# Step 3: Generate PNG using BoxWatcher
echo ""
echo "🖼️  Step 3: Generating PNG..."

# Create temporary builds.csv for PNG generator
TEMP_BUILDS="$PROJECT_DIR/output/.temp-builds.csv"
echo "name,command,enabled" > "$TEMP_BUILDS"
echo "$OUTPUT_NAME,dummy,true" >> "$TEMP_BUILDS"

# Run PNG generator with project's node_modules
if [ -f "$SCRIPT_DIR/../boxwatcher/generate-pngs.js" ]; then
    cd "$PROJECT_DIR"
    NODE_PATH="$PROJECT_DIR/node_modules:$NODE_PATH" node -e "
        const { loadConfig } = require('$SCRIPT_DIR/../boxwatcher/config');
        const { main } = require('$SCRIPT_DIR/../boxwatcher/generate-pngs');

        // Override config to use temp builds file
        const config = loadConfig();
        config.paths.builds = '$TEMP_BUILDS';

        main(config).catch(console.error);
    "
    rm -f "$TEMP_BUILDS"
else
    echo "⚠️  BoxWatcher PNG generator not found"
    echo "   PNG generation skipped"
fi

echo ""
echo "✅ Done!"
echo ""
echo "Generated files:"
echo "  📄 $POSITIONED_YAML"
echo "  🖼️  $PROJECT_DIR/output/$OUTPUT_NAME.svg"
if [ -f "$PROJECT_DIR/output/$OUTPUT_NAME.png" ]; then
    echo "  🖼️  $PROJECT_DIR/output/$OUTPUT_NAME.png"
fi
