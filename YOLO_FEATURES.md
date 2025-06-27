# YOLO Integration in RedLabel

RedLabel now includes powerful YOLO model integration for automatic image annotation, making it faster to label large datasets.

## Features

### 1. YOLO as Default Format
- YOLO format is now the default annotation format when starting RedLabel
- Normalized coordinates (0-1) for better model compatibility
- Automatic class index management

### 2. YOLO Model Integration
- **Automatic Model Detection**: RedLabel scans for `.pt` model files in the application directory
- **Model Selection Dialog**: Browse and select YOLO models with confidence threshold settings
- **Batch Inference**: Run inference on all unlabeled images in a directory
- **Smart Processing**: Only processes images that don't have existing label files

### 3. Requirements & Setup

#### Prerequisites
- Python 3.8+
- ultralytics package: `pip install ultralytics`
- YOLO model file (`.pt` format)
- Directory with images
- Defined save directory with `labels.txt` file

#### Directory Structure
```
your_project/
├── redlabel.py
├── your_model.pt          # Place YOLO model here
├── images/                # Directory with images
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
└── labels/                # Save directory
    ├── labels.txt         # Class names (one per line)
    ├── image1.txt         # Generated YOLO labels
    └── image2.txt
```

## Usage Guide

### Step 1: Setup
1. **Install Dependencies**:
   ```bash
   pip install ultralytics
   ```

2. **Prepare YOLO Model**:
   - Place your `.pt` model file in the same directory as `redlabel.py`
   - Or use the browse button to select a model from anywhere

3. **Create Labels File**:
   - Create a `labels.txt` file in your save directory
   - List class names (one per line) matching your model's classes
   - Example provided in `data/labels.txt`

### Step 2: Open Directory and Configure
1. **Open Image Directory**: File → Open Dir (Ctrl+U)
2. **Set Save Directory**: File → Change Save Dir (Ctrl+R)
3. **Select YOLO Model**: Click "Select Model" in the sidebar
   - Choose your `.pt` file
   - Set confidence threshold (default: 0.25)
   - Click OK

### Step 3: Run Inference
1. **Check Requirements**: The "Run YOLO Inference" button will be enabled when:
   - ✓ Model is selected and loaded
   - ✓ Directory of images is open (not single image mode)
   - ✓ Save directory is defined
   - ✓ `labels.txt` exists in save directory

2. **Start Inference**: Click "Run YOLO Inference"
   - Confirms the number of unlabeled images
   - Shows progress bar during processing
   - Creates `.txt` label files for detected objects

3. **Review Results**: 
   - Labels appear automatically on the current image
   - Navigate through images to review/edit detections
   - Make manual corrections as needed

## UI Components

### Sidebar Controls
- **Select Model Button**: Opens model selection dialog
- **Model Status Label**: Shows currently selected model
- **Run YOLO Inference Button**: Starts batch inference process
- **Progress Bar**: Shows inference progress (hidden when not running)

### Model Selection Dialog
- **Available Models List**: Shows `.pt` files in application directory
- **Browse Button**: Select models from other locations
- **Confidence Threshold**: Adjust detection sensitivity (0.01-1.0)
- **Model Info**: Displays selected model details

## Technical Details

### YOLO Format
RedLabel uses the standard YOLO format:
```
class_index x_center y_center width height
```
- All coordinates are normalized (0-1)
- `class_index`: Integer index from `labels.txt`
- Center coordinates and dimensions are relative to image size

### Inference Pipeline
1. **Image Processing**: Each unlabeled image is processed individually
2. **Detection**: YOLO model returns bounding boxes, confidence scores, and class IDs
3. **Filtering**: Detections below confidence threshold are discarded
4. **Conversion**: Pixel coordinates converted to normalized YOLO format
5. **Class Mapping**: Model class names mapped to indices from `labels.txt`
6. **File Creation**: YOLO format `.txt` file created for each image

### Background Processing
- Inference runs in separate thread to avoid UI freezing
- Progress updates in real-time
- Failed inferences are logged but don't stop the process
- Current image updates automatically if processed

## Error Handling

### Common Issues and Solutions

**"ultralytics package is required"**
- Install with: `pip install ultralytics`

**"No models found in application directory"**
- Place `.pt` file in same directory as `redlabel.py`
- Use "Browse" button to select model from another location

**Button disabled/grayed out:**
- Check all requirements are met (see Step 3 above)
- Ensure you're in directory mode (not single image)
- Verify `labels.txt` exists in save directory

**"All images already have label files"**
- Delete existing `.txt` files you want to regenerate
- Or manually create new unlabeled images

**Model loading fails:**
- Verify `.pt` file is valid YOLO model
- Check model compatibility with ultralytics version
- Ensure sufficient system memory

## Tips for Best Results

1. **Model Selection**: Use models trained on similar data to your images
2. **Confidence Threshold**: 
   - Lower (0.1-0.3): More detections, may include false positives
   - Higher (0.5-0.8): Fewer, more confident detections
3. **Class Management**: Keep `labels.txt` consistent with your model's classes
4. **Review Process**: Always review and manually correct auto-generated labels
5. **Iterative Workflow**: Use inference for initial labeling, then manual refinement

## Integration with Existing Workflow

The YOLO integration seamlessly works with RedLabel's existing features:
- **Format Switching**: Still supports PASCAL VOC and CreateML formats
- **Manual Editing**: Edit auto-generated labels normally
- **Keyboard Shortcuts**: All existing shortcuts work
- **Save/Export**: Standard save functionality works with YOLO labels
- **Verification**: Mark images as verified after review

## Performance Notes

- **Speed**: Inference speed depends on model size and hardware
- **Memory**: Large models may require significant GPU/CPU memory
- **Batch Size**: Images processed individually for memory efficiency
- **Threading**: UI remains responsive during inference

This integration makes RedLabel a powerful tool for both manual annotation and AI-assisted labeling workflows.
