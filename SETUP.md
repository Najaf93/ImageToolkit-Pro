# Setup Guide - Image to Canvas Converter

## First-Time Setup

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- **Pillow**: Image processing
- **rembg**: Background removal with AI

### Step 2: First Run (Background Model Download)

The first time you use the "Remove Background" feature, `rembg` will download the AI model (~350MB). This is a one-time download.

```bash
python image_converter.py
```

**Note**: The first background removal may take 1-2 minutes as the model is downloaded and initialized.

## Running the Application

```bash
python image_converter.py
```

## Troubleshooting

### Issue: "rembg" import not found
**Solution**: Run `pip install -r requirements.txt` again

### Issue: Background removal is very slow
**Solution**: 
- First run downloads the model (~350MB) - subsequent runs will be faster
- Ensure you have at least 2GB free disk space
- The feature works best with GPU acceleration (if your system has NVIDIA/AMD GPU)

### Issue: "ONNX Runtime" errors
**Solution**: Install ONNX Runtime separately:
```bash
pip install onnxruntime
```

Or for GPU support:
```bash
pip install onnxruntime-gpu
```

### Issue: Memory issues with large images
**Solution**: The app works best with images under 4000x4000 pixels. Resize very large images first.

## Performance Tips

1. **Faster Background Removal**: 
   - Resize images to around 1200x1200 before removing background for faster processing
   - Use the zoom slider after removal to adjust framing

2. **Batch Processing**: 
   - For multiple images, the app loads the model once and reuses it
   - Processing subsequent images will be much faster

3. **File Format**:
   - Use PNG for best quality when saving with transparent background
   - Use JPEG for smaller file sizes with white background

## System Requirements

- **Python**: 3.7 or higher
- **RAM**: Minimum 2GB (4GB+ recommended for smooth background removal)
- **Disk Space**: At least 500MB free (for rembg model)
- **GPU** (Optional): NVIDIA or AMD GPU for faster background removal

## Advanced: GPU Acceleration

For NVIDIA GPU users:

```bash
pip install onnxruntime-gpu
```

For AMD/DirectML:

```bash
pip install onnxruntime-directml
```

This will significantly speed up background removal operations.
