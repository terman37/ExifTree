# ExifTree 📷

ExifTree is a command-line tool that automatically organizes photos and videos into a structured folder hierarchy based on their EXIF and QuickTime metadata. Perfect for managing large photo libraries with automatic date-based organization.

## ✨ Features

- **Metadata-Driven Organization:** Reads creation dates from EXIF metadata (`EXIF:DateTimeOriginal`) and QuickTime metadata (`QuickTime:CreateDate`), organizing files by year/month/day
- **Flexible File Actions:** Supports both `copy` and `move` operations
- **Dry-Run Safety:** Preview all operations before executing them—perfect for testing configurations
- **Intelligent Filtering:** 
  - Resolution filtering (skip images below size thresholds)
  - File extension filtering
  - Multiple destination paths for organized/unknown/duplicate files
- **Recursive Scanning:** Scan multiple input directories with configurable depth
- **Docker Ready:** Fully containerized with Docker and Docker Compose support

---

## 📋 Prerequisites

### System Requirements

- **Python 3.13+** (for local development)
- **exiftool** (required for all metadata extraction)

### Installing exiftool

- **Ubuntu/Debian:**
  ```bash
  sudo apt-get install exiftool
  ```
- **macOS (via Homebrew):**
  ```bash
  brew install exiftool
  ```
- **Windows:** Download from [exiftool.org](https://exiftool.org) or use `choco install exiftool`

---

## ⚙️ Configuration

ExifTree reads settings from `./config/config.yaml` on startup. You can override the config file location using the `EXIFTREE_CONFIG_FILE` environment variable.

### Configuration Structure (`config.yaml`)

```yaml
# Global operational settings
global_settings:
  log_level: INFO          # Logging level: DEBUG, INFO, WARNING, ERROR
  dry_run: true            # If true, preview operations without executing
  write_metadata_from_filename: false  # If true, write filename-derived date into file metadata

# File action: "copy" or "move"
action: copy

# Input directories to scan
input_folders:
  - path: data/input
    max_depth: 1           # Recursion depth (1 = direct children only)

# Output folder configuration with template variables
output_folder:
  base_path_template: "data/output/{year}/{month}"    # Main organized path
  unknown_path_template: "data/output/unknown"         # Files with no date metadata
  duplicates_path_template: "data/output/duplicates/{year}/{month}"  # Duplicate files

# File filtering options
file_filters:
  min_width: 600           # Minimum image width (0 to disable)
  min_height: 600          # Minimum image height (0 to disable)
  extensions:              # File extensions to process (case-insensitive)
    - jpg
    - jpeg
    - png
    - mp4
    - mov
    - mpg
    - wmv
    - avi
    - 3gp
```

### Template Variables

Use the following variables in path templates:
- `{year}` — 4-digit year (e.g., 2024)
- `{month}` — 2-digit month (e.g., 06)
- `{day}` — 2-digit day (e.g., 15)

---

## 🚀 Quick Start

### 1. Setup (Local Development)

Clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/ExifTree.git
cd ExifTree
uv sync
```

### 2. Configure

Edit `./config/config.yaml` to set your input/output directories and preferences.

### 3. Run (Dry-Run First!)

Always test with dry-run enabled before executing:

```bash
uv run python -m exiftree.main
```

Once you've verified the output, disable `dry_run: true` in your config or override via CLI:

```bash
uv run python -m exiftree.main --dry_run false
```

---

## 📖 Usage

### Basic Command

```bash
uv run python -m exiftree.main
```

This runs ExifTree with settings from `./config/config.yaml`.

### Command-Line Overrides

Override any config setting directly from the CLI:

```bash
# Test with dry-run before executing
uv run python -m exiftree.main --dry_run true

# Switch to move instead of copy
uv run python -m exiftree.main --action move

# Apply strict resolution filtering
uv run python -m exiftree.main --min_width 1920 --min_height 1080

# Increase logging verbosity
uv run python -m exiftree.main --log_level DEBUG
```

### Help

View all available options:

```bash
uv run python -m exiftree.main --help
```

---

## 🐳 Docker Execution

### Build the Image

```bash
docker build -t exiftree:latest .
```

### Using Docker Run

Map your photos, output, and config into the container:

```bash
docker run --rm \
  -v $(pwd)/config/config.yaml:/app/config/config.yaml \
  -v /path/to/my/photos:/data/input \
  -v /path/to/sorted/photos:/data/output \
  exiftree:latest
```

### Using Docker Compose (Recommended)

Simplest approach—just prepare your files and run:

1. Place input photos in `./data/input/`
2. Run the service:
   ```bash
   docker compose build
   docker compose run --rm exiftree
   ```

Output will be organized in `./data/output/`.

---

## 📁 Project Structure

```
ExifTree/
├── README.md                    # This file
├── pyproject.toml              # Python project metadata
├── uv.lock                     # Dependency lock file
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Docker Compose configuration
├── config/
│   └── config.yaml             # Main configuration file
├── data/
│   ├── input/                  # Photos to be organized (source)
│   └── output/                 # Organized output directory
└── src/exiftree/
    ├── main.py                 # Application entry point
    ├── config.py               # Configuration parsing (Pydantic)
    ├── media.py                # Media file metadata handling
    ├── process_files.py        # Core file processing logic
    └── utils.py                # Utility functions
```

---

## 🔍 How It Works

1. **Scan** — Recursively scans input directories for media files
2. **Filter** — Applies extension and resolution filters
3. **Extract Metadata** — Reads creation dates using `exiftool`
4. **Organize** — Determines destination path based on date and templates
5. **Execute** — Copies or moves files (or previews in dry-run mode)
6. **Report** — Logs operations and handles errors intelligently

---

## 🛠️ Development

### Running Tests

```bash
uv run pytest
```

### Code Quality

Project uses `ruff` for linting and `mypy` for type checking:

```bash
uvrun ruff check src/
uv run mypy src/
```

