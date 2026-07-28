TODO: 
- add group functionality
- GUI

# bratt - Bad Roblox Asset Texture Taker

A Python tool for downloading Roblox catalog item textures (shirts/pants) via Roblox's API, with optional template overlay functionality.

## Features

- Download shirt and pants textures from Roblox catalog URLs or asset IDs
- Batch processing from text files
- Automatic detection of matching clothing sets (shirt+pants pairs)
- Template overlay support for custom backgrounds
- Single-file executable distribution option

## Requirements

- Python 3.12+
- Roblox API key with 'legacy-assets' read permission
- Dependencies: requests, pillow, rich (see requirements.txt)

## Installation

### Option 1: Single-File Executable (Recommended)

Download the latest `bratt.py` from [releases](https://github.com/yourrepo/rbx-scrape/releases):

```bash
# Download
wget https://github.com/yourrepo/rbx-scrape/releases/latest/download/bratt.py

# Run directly (no installation needed!)
python bratt.py <roblox_catalog_url_or_id>
```

**First run extracts dependencies to cache (~2-3 seconds), subsequent runs are instant.**

### Option 2: From Source

```bash
# Clone repository
git clone https://github.com/yourrepo/rbx-scrape.git
cd rbx-scrape

# Install dependencies
pip install -r requirements.txt

# Run
python bratt/main.py <roblox_catalog_url_or_id>
```

## Setup

1. Create `api_key.txt` in the project root with your Roblox API key:
   ```
   your-api-key-here
   ```

2. (Optional) Add `template.png` for overlay functionality

3. (Optional) Create `links.txt` for batch processing (one URL/ID per line)

## Usage

### Single Asset Download

```bash
python bratt.py https://www.roblox.com/catalog/123456789/Item-Name
# or
python bratt.py 123456789
```

### Batch Processing

```bash
# Using default links.txt
python bratt.py -b

# Using custom file
python bratt.py -b my_links.txt
```

### With Template Overlay

```bash
# Single item with overlay
python bratt.py -o https://www.roblox.com/catalog/123456789/Item-Name

# Batch with overlay
python bratt.py -b -o links.txt

# Apply overlay to existing textures
python bratt.py bg-replace
```

### SFX Commands (Single-File Executable Only)

```bash
# Show version and build information
python bratt.py --sfx-info

# Clean cache directory
python bratt.py --sfx-clean
```

## Output Structure

```
textures/
├── Shirt/           # Downloaded shirt textures
├── Pants/           # Downloaded pants textures
├── e_shirt/         # Overlayed shirts (with template)
└── e_pants/         # Overlayed pants (with template)
```

## Building Single-File Executable

```bash
# Activate virtual environment
. ./.venv/bin/activate

# Run build script
./scripts/make-sfx.sh

# Output: dist/bratt.py (~3-4MB)
```

## How It Works

1. Extracts asset ID from Roblox URL or validates provided ID
2. Fetches asset details via Roblox API
3. Downloads XML model file containing texture references
4. Extracts and downloads actual texture images
5. Automatically finds matching shirt/pants pairs
6. Optionally applies template overlay

## API Key

Get a Roblox API key from [Roblox Creator Dashboard](https://create.roblox.com/):
- Navigate to API Keys
- Create new key with 'legacy-assets' read permission
- Save to `api_key.txt` in project root

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
