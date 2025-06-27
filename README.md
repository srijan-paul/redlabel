# RedLabel

A modern fork of the popular LabelImg image annotation tool with quality of life improvements.

![Demo](demo/demo.jpg)

## Features

- **Multiple formats**: PASCAL VOC XML, YOLO, CreateML
- **Cross-platform**: Windows, macOS, Linux
- **Keyboard shortcuts** for efficient labeling
- **Pre-defined classes** support
- **Verification mode** for dataset validation

## Quick Start

### Installation

```bash
# Install from PyPI
pip install redlabel

# Or install from source
git clone https://github.com/srijan-paul/RedLabel.git
cd RedLabel
pip install -e .
```

### Usage

```bash
# Launch the application
redlabel

# Or with specific image/classes
redlabel [IMAGE_PATH] [CLASS_FILE]
```

## Development

```bash
# Clone and setup
git clone https://github.com/srijan-paul/RedLabel.git
cd RedLabel
pip install -r requirements.txt
pip install -e .[dev]

# Build resources
make qt5py3

# Run tests
make test

# Run application
python3 redlabel.py
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
