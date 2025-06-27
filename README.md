# RedLabel

A modern fork of the popular image annotation tool with quality of life improvements.

![Demo](demo/demo.jpg)

## Features

- **Multiple formats**: PASCAL VOC XML, YOLO, CreateML
- **Cross-platform**: Windows, macOS, Linux
- **Keyboard shortcuts** for efficient labeling
- **Pre-defined classes** support
- **Verification mode** for dataset validation

## Quick Start

### Installation

First, install [uv](https://astral.sh/uv) - the fast Python package manager:

```bash
# Install uv (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then install RedLabel:

```bash
git clone https://github.com/srijan-paul/RedLabel.git
cd RedLabel
uv sync
```

### Usage

```bash
# Launch the application
uv run redlabel.py
uv run redlabel.py [IMAGE_PATH] [CLASS_FILE]
```

## Development

```bash
# Clone and setup
git clone https://github.com/srijan-paul/RedLabel.git
cd RedLabel

# Install dependencies and create virtual environment
uv sync --dev

# Build resources
uv run make qt5py3

# Run tests
uv run make test

# Run application
uv run python redlabel.py
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `w` | Create bounding box |
| `d` | Next image |
| `a` | Previous image |
| `Ctrl+s` | Save |
| `Space` | Mark as verified |
| `Del` | Delete selected box |

## Supported Formats

- **PASCAL VOC**: XML format (ImageNet compatible)
- **YOLO**: TXT format for YOLO training
- **CreateML**: JSON format for Apple's CreateML

## Credits

This is a modernized fork of [HumanSignal/labelImg](https://github.com/HumanSignal/labelImg) 
(originally by TzuTa Lin) with improved setup process and quality of life features.

## License

MIT License - see [LICENSE](LICENSE) for details.
