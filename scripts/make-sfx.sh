#!/bin/bash
set -e

echo "Building single-file executable for bratt..."

# Configuration
COMPRESSION="${1:-bz2}"  # bz2, gz, or xz
SFX_DIR="sfx"
DIST_DIR="dist"
OUTPUT_FILE="$DIST_DIR/bratt.py"

# Clean previous builds
rm -rf "$SFX_DIR" "$DIST_DIR"
mkdir -p "$SFX_DIR" "$DIST_DIR"

# Locate python from venv or fallback to system
if [ -f ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
else
    echo "Warning: Virtual environment not found at .venv/"
    PYTHON="python"
fi

echo "Using Python: $($PYTHON --version)"

# Install dependencies to sfx directory using uv or pip
echo "Installing dependencies..."
if command -v uv &>/dev/null; then
    uv pip install --python "$PYTHON" -t "$SFX_DIR" -r requirements.txt -q
elif "$PYTHON" -m pip --version &>/dev/null 2>&1; then
    "$PYTHON" -m pip install -t "$SFX_DIR" -r requirements.txt -q
else
    echo "Error: Neither uv nor pip found. Install one to bundle dependencies."
    exit 1
fi

# Copy bratt modules
echo "Copying bratt modules..."
cp -r bratt/ "$SFX_DIR/bratt/"

# Optimize bundle
echo "Optimizing bundle size..."
find "$SFX_DIR" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find "$SFX_DIR" -type f -name "*.pyc" -delete
find "$SFX_DIR" -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find "$SFX_DIR" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find "$SFX_DIR" -type d -name tests -exec rm -rf {} + 2>/dev/null || true
find "$SFX_DIR" -type d -name test -exec rm -rf {} + 2>/dev/null || true

# Create tar archive
echo "Creating archive..."
cd "$SFX_DIR"
tar -cf ../archive.tar .
cd ..

# Compress archive
case "$COMPRESSION" in
    bz2)
        echo "Compressing with bzip2..."
        bzip2 -9 archive.tar
        ARCHIVE_FILE="archive.tar.bz2"
        COMP_TYPE="bz2"
        ;;
    gz)
        echo "Compressing with gzip..."
        gzip -9 archive.tar
        ARCHIVE_FILE="archive.tar.gz"
        COMP_TYPE="gz"
        ;;
    xz)
        echo "Compressing with xz..."
        xz -9 archive.tar
        ARCHIVE_FILE="archive.tar.xz"
        COMP_TYPE="xz"
        ;;
    *)
        echo "Unknown compression: $COMPRESSION"
        exit 1
        ;;
esac

# Calculate checksum
CHECKSUM=$(shasum -a 256 "$ARCHIVE_FILE" | awk '{print $1}')
echo "Archive checksum: $CHECKSUM"

# Encode archive to base64
echo "Encoding archive..."
BASE64_DATA=$(base64 < "$ARCHIVE_FILE" | tr -d '\n')

# Get version from git or default
VERSION=$(git describe --tags 2>/dev/null || echo "dev")
BUILD_DATE=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

# Create output file with bootstrap + data
echo "Creating single-file executable..."
cat > "$OUTPUT_FILE" << 'BOOTSTRAP_EOF'
#!/usr/bin/env python3
"""
bratt - Bad Roblox Asset Texture Taker (Single-file executable)
Roblox texture downloader with optional template overlay

This is a self-extracting archive. Run with --sfx-info for details.
"""

import os
import sys
import tarfile
import tempfile
import base64
import hashlib
import shutil
from pathlib import Path

# Metadata
VERSION = "VERSION_PLACEHOLDER"
BUILD_DATE = "BUILD_DATE_PLACEHOLDER"
COMPRESSION = "COMP_TYPE_PLACEHOLDER"
CHECKSUM = "CHECKSUM_PLACEHOLDER"

def get_cache_dir():
    """Get platform-specific cache directory."""
    if sys.platform == "win32":
        cache_base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        return os.path.join(cache_base, "bratt")
    else:
        cache_base = os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
        return os.path.join(cache_base, "bratt")

def verify_checksum(data):
    """Verify archive integrity."""
    actual = hashlib.sha256(data).hexdigest()
    if actual != CHECKSUM:
        raise ValueError(f"Checksum mismatch! Expected {CHECKSUM}, got {actual}")

def extract_archive():
    """Extract embedded archive to cache directory."""
    cache_dir = get_cache_dir()
    version_file = os.path.join(cache_dir, ".version")

    # Check if already extracted and current
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            cached_version = f.read().strip()
        if cached_version == f"{VERSION}-{CHECKSUM[:8]}":
            print(f"Using cached extraction: {cache_dir}", file=sys.stderr)
            return cache_dir

    # Clean old extraction
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)

    print(f"Extracting to: {cache_dir}", file=sys.stderr)
    os.makedirs(cache_dir, exist_ok=True)

    # Decode and verify archive
    archive_data = base64.b64decode(ARCHIVE_DATA)
    verify_checksum(archive_data)

    # Extract archive
    with tempfile.NamedTemporaryFile(suffix=f'.tar.{COMPRESSION}', delete=False) as tmp:
        tmp.write(archive_data)
        tmp_path = tmp.name

    try:
        with tarfile.open(tmp_path, f'r:{COMPRESSION}') as tar:
            # Use filter='data' for Python 3.12+, fallback for older versions
            if hasattr(tarfile, 'data_filter'):
                tar.extractall(cache_dir, filter='data')
            else:
                tar.extractall(cache_dir)

        # Write version marker
        with open(version_file, 'w') as f:
            f.write(f"{VERSION}-{CHECKSUM[:8]}")

        return cache_dir
    finally:
        os.unlink(tmp_path)

def show_info():
    """Show SFX information."""
    print(f"bratt Single-File Executable")
    print(f"Version: {VERSION}")
    print(f"Build Date: {BUILD_DATE}")
    print(f"Compression: {COMPRESSION}")
    print(f"Checksum: {CHECKSUM}")
    print(f"Cache Directory: {get_cache_dir()}")
    print(f"Python: {sys.version}")

def clean_cache():
    """Remove cached extraction."""
    cache_dir = get_cache_dir()
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        print(f"Removed cache: {cache_dir}")
    else:
        print("Cache directory not found")

def main():
    """Main entry point."""
    # Handle SFX-specific flags
    if '--sfx-info' in sys.argv:
        show_info()
        return 0

    if '--sfx-clean' in sys.argv:
        clean_cache()
        return 0

    # Extract and setup paths
    extract_path = extract_archive()

    # Remove this script's own directory from sys.path to prevent the SFX file
    # itself (bratt.py) from being imported as the 'bratt' module.
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    if script_dir in sys.path:
        sys.path.remove(script_dir)
    sys.path.insert(0, extract_path)

    # Import and run bratt
    try:
        from bratt.main import main as bratt_main
        bratt_main()
    except ImportError as e:
        print(f"Error importing bratt: {e}", file=sys.stderr)
        print(f"Extract path: {extract_path}", file=sys.stderr)
        return 1

# eof
ARCHIVE_DATA = """
BOOTSTRAP_EOF

# Append base64 data
echo "$BASE64_DATA" >> "$OUTPUT_FILE"

# Close the string and entry point (after ARCHIVE_DATA is defined)
cat >> "$OUTPUT_FILE" << 'EOF'
"""

if __name__ == "__main__":
    sys.exit(main() or 0)
EOF

# Replace placeholders
sed -i.bak "s/VERSION_PLACEHOLDER/$VERSION/" "$OUTPUT_FILE"
sed -i.bak "s/BUILD_DATE_PLACEHOLDER/$BUILD_DATE/" "$OUTPUT_FILE"
sed -i.bak "s/COMP_TYPE_PLACEHOLDER/$COMP_TYPE/" "$OUTPUT_FILE"
sed -i.bak "s/CHECKSUM_PLACEHOLDER/$CHECKSUM/" "$OUTPUT_FILE"
rm "$OUTPUT_FILE.bak" 2>/dev/null || true

# Make executable
chmod +x "$OUTPUT_FILE"

# Clean up
rm -f "$ARCHIVE_FILE"

# Show results
FILE_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE")
FILE_SIZE_MB=$(echo "scale=2; $FILE_SIZE / 1024 / 1024" | bc 2>/dev/null || echo "N/A")

echo ""
echo "Build complete!"
echo "Output: $OUTPUT_FILE"
echo "Size: ${FILE_SIZE_MB}MB"
echo ""
echo "Test with: python $OUTPUT_FILE --help"
echo "Show info: python $OUTPUT_FILE --sfx-info"
echo "Clean cache: python $OUTPUT_FILE --sfx-clean"
