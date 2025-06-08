# Image Directory Index Generator

This script generates thumbnail index images for directories containing images. It is specifically designed to work with photo collections organized in a YYYY/YYYY-MM/YYYY-MM-DD directory structure, creating monthly index thumbnails for all photos.

## Features

- Creates monthly index thumbnails from YYYY/YYYY-MM/YYYY-MM-DD directory structure
- Supports common image formats (JPG, PNG, GIF, BMP, WebP)
- Supports raw image formats (CR2, NEF, ARW, ORF, RW2, RAF, DNG)
- Creates paginated index images for months with many photos
- Configurable thumbnail size and layout
- Displays filenames under each thumbnail
- Frames around thumbnails for better visibility
- Progress logging and error handling
- Option to output index files to a separate directory

## Prerequisites

1. Python 3.6+
2. ImageMagick (must be installed on your system)
   - For raw file support, ensure ImageMagick is installed with raw image delegates

   ```bash
   # For macOS using Homebrew
   brew install imagemagick --with-raw
   
   # For Ubuntu/Debian
   sudo apt-get install imagemagick libraw-dev
   ```

3. Python packages listed in requirements.txt

## Installation

1. Install ImageMagick on your system:

   ```bash
   # For macOS using Homebrew
   brew install imagemagick

   # For Ubuntu/Debian
   sudo apt-get install imagemagick

   # For Windows
   # Download and install from https://imagemagick.org/script/download.php
   ```

2. Set up a Python virtual environment (recommended):

   ```bash
   # Create virtual environment
   python3 -m venv venv

   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```bash
python generate_index.py /path/to/your/photos
```

This will:

- Scan the directory structure (YYYY/YYYY-MM/YYYY-MM-DD)
- Create monthly index thumbnails
- Use default settings (10 thumbnails per row, 150x150 pixel thumbnails)
- Place index files in respective year directories

### Advanced Options

```bash
python generate_index.py /path/to/photos \
    --thumbnails-per-row 12 \
    --thumbnail-width 140 \
    --thumbnail-height 140 \
    --max-thumbnails 300 \
    --output-dir /path/to/indexes
```

### Available Options

- `--thumbnails-per-row`: Number of thumbnails per row (default: 10)
- `--thumbnail-width`: Width of each thumbnail in pixels (default: 150)
- `--thumbnail-height`: Height of each thumbnail in pixels (default: 150)
- `--max-thumbnails`: Maximum number of thumbnails per index image (default: 200)
- `--output-dir`: Optional output directory for index files

## Output File Names

The script generates index files based on the year-month structure:

```text
Source Directory Structure:
/photos/
  └── 2024/
      ├── 2024-01/
      │   ├── 2024-01-01/
      │   └── 2024-01-02/
      └── 2024-02/
          ├── 2024-02-01/
          └── 2024-02-02/

Generated Index Files:
Without --output-dir:
/photos/2024/index_2024-01.jpg
/photos/2024/index_2024-02.jpg

With --output-dir specified:
/path/to/indexes/index_2024-01.jpg
/path/to/indexes/index_2024-02.jpg

For months with many images (pagination):
index_2024-01.jpg          # Single page
index_2024-02_001.jpg      # First page of multi-page month
index_2024-02_002.jpg      # Second page
index_2024-02_003.jpg      # Third page
```

## Examples

1. Basic usage with defaults:

   ```bash
   python generate_index.py ~/Photos
   ```

2. Create denser thumbnails for a large collection:

   ```bash
   python generate_index.py ~/Photos \
       --thumbnails-per-row 12 \
       --thumbnail-width 120 \
       --thumbnail-height 120
   ```

3. Output all index files to a separate directory:

   ```bash
   python generate_index.py ~/Photos --output-dir ~/Photos/indexes
   ```

4. Handle large collections with more thumbnails per page:

   ```bash
   python generate_index.py ~/Photos \
       --max-thumbnails 300 \
       --thumbnails-per-row 15
   ```

## Layout Guidelines

When choosing the number of columns and thumbnail sizes, consider:

1. Screen Resolution:
   - For 1080p displays: 8-12 columns work well
   - For 4K displays: 12-20 columns are possible
   - For printing: You can go up to 20-25 columns

2. Thumbnail Sizes:
   - Large (200px): Good for detailed preview, 5-6 columns
   - Medium (150px): Good balance, 10-12 columns
   - Small (120px): Dense layout, 12-15 columns
   - Very small (100px): Contact sheet style, 15-20+ columns

3. Recommended Combinations:
   - Standard Preview: 10 columns × 150px (default)
   - Dense Preview: 12 columns × 120px
   - Contact Sheet: 20 columns × 100px
   - Detailed Preview: 6 columns × 200px

## Troubleshooting

1. If you get ImageMagick policy errors:
   - Edit the ImageMagick policy file (`/etc/ImageMagick-6/policy.xml` or similar)
   - Modify or remove the line containing `<policy domain="resource" name="memory" value="256MiB"/>`

2. If thumbnails appear blurry:
   - Increase the thumbnail dimensions using `--thumbnail-width` and `--thumbnail-height`

3. If processing is slow:
   - Reduce `--max-thumbnails` to process fewer images per page
   - Reduce thumbnail dimensions
   - Ensure you have enough system memory available

## Notes

- The script maintains aspect ratios when creating thumbnails
- File names longer than 25 characters are truncated with "..."
- Progress is logged to the console during processing
- Errors are logged but won't stop the entire process
- Supported image formats depend on your ImageMagick installation
