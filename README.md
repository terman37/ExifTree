# ExifTree

ExifTree is a tool to organize photos and videos into a structured folder hierarchy (e.g. `YYYY/MM/DD`) based on EXIF and QuickTime creation dates.

## Features

- **Metadata-Driven Organization:** Automatically reads creation dates from EXIF metadata (`EXIF:DateTimeOriginal`) and QuickTime metadata (`QuickTime:CreateDate`).
- **Flexible File Actions:** Supports both copying (`copy`) and moving (`move`) operations.
- **Dry-Run Safety:** Validate and preview operations before writing any files.
- **Resolution Filtering:** Automatically skip images below a minimum width and height threshold.
- **Recursive Scanning:** Scan multiple input directories with configurable search depths.
- **Docker Ready:** Outputs structured logs designed for containerized environments.

---

## Prerequisites

ExifTree relies on the `exiftool` command-line application to extract file metadata.

### Installation

- **Ubuntu/Debian:**
  ```bash
  sudo apt-get install exiftool
  ```
- **macOS (via Homebrew):**
  ```bash
  brew install exiftool
  ```

---

## Configuration

ExifTree reads its default settings from `./config/config.yaml`. You can specify a different configuration file path using the `EXIFTREE_CONFIG_FILE` environment variable.

### Configuration Structure (`config.yaml`)

```yaml
# Directories to scan for files
input_folders:
  - path: data/input
    max_depth: 1

# Destination directory and path template details
output_folder:
  base_path: "data/output"
  # Available template variables: {year}, {month}, {day}
  template: "{year}/{month}/{day}"

# Operational options
global_settings:
  log_level: "info"     # logging level (debug, info, warning, error)
  dry_run: false        # if true, log operations without executing them

action: "copy"          # "copy" or "move"

file_filters:
  # Image size filter (0 to disable)
  min_width: 0
  min_height: 0
  # List of file extensions to scan (case-insensitive)
  extensions:
    - jpg
    - jpeg
    - png
    - mp4
    - mov
```

---

## Usage

ExifTree is developed using Python 3.13 and managed via `uv`.

### Running Locally

To run ExifTree with the configuration file:
```bash
uv run python -m exiftree.main
```

### CLI Overrides

All settings in `config.yaml` can be overridden directly from the command line:

- **Run a dry-run move simulation:**
  ```bash
  uv run python -m exiftree.main --dry_run true --action move
  ```
- **Set a minimum dimension filter:**
  ```bash
  uv run python -m exiftree.main --min_width 1920 --min_height 1080
  ```
- **Review CLI options:**
  ```bash
  uv run python -m exiftree.main --help
  ```

---

## Docker Execution

### Using Docker Run

To run ExifTree inside a Docker container, map your input, output, and configuration files into the container volumes:

```bash
docker run --rm \
  -v $(pwd)/config/config.yaml:/app/config/config.yaml \
  -v /path/to/my/photos:/data/input \
  -v /path/to/sorted/photos:/data/output \
  exiftree:latest
```

### Using Docker Compose

Alternatively, you can build and run ExifTree using Docker Compose:

1. Place your input files in `./data/input/`.
2. Run the compose service:
   ```bash
   docker compose run --rm exiftree
   ```

