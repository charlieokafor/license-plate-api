# License Plate API

Small FastAPI service that detects license plates in an image using YOLO (Ultralytics) and extracts text using EasyOCR. The server returns any detected plate texts and a processed image (with detection boxes and OCR labels) encoded as a base64 JPEG.

This README explains how to set up, run, and use the API found in `main.py`.

## Features
- YOLO-based plate detection (default uses `yolov8n.pt`)
- OCR on detected plate crops using EasyOCR
- Returns:
  - `plates`: list of recognized plate texts
  - `processed_image_base64`: JPEG image (base64) with drawn boxes/labels
- CORS enabled (for testing)

## Requirements
- Python 3.8+
- Torch (CPU or CUDA build — see Troubleshooting)
- The following Python libraries (example install below):
  - fastapi
  - uvicorn
  - numpy
  - opencv-python-headless (or opencv-python)
  - easyocr
  - ultralytics
  - pillow
  - requests (for examples)

Note: EasyOCR and Ultralytics depend on torch. Installing the correct `torch` wheel for your system (and CUDA version if you want GPU acceleration) is important.

## Installation (basic)
1. Clone the repo:
   ```bash
   git clone https://github.com/charlieokafor/license-plate-api.git
   cd license-plate-api
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux / macOS
   .venv\Scripts\activate      # Windows (cmd)
   ```

3. Install dependencies:
   - Install a suitable `torch` first (follow https://pytorch.org/get-started/locally/). Example for CPU-only:
     ```bash
     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
     ```
   - Then install the rest:
     ```bash
     pip install fastapi uvicorn numpy opencv-python-headless pillow easyocr ultralytics
     ```
   Alternatively, create a `requirements.txt` with the packages above and run `pip install -r requirements.txt`.

4. Place or point to your YOLO model:
   - By default the code loads `yolov8n.pt`:
     - If you want a custom license-plate trained model, replace `yolov8n.pt` or change the path in `main.py`:
       ```py
       model = YOLO("path/to/your_custom_plate_model.pt")
       ```

## Run the API
Run the FastAPI app using uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: http://127.0.0.1:8000

Visit the interactive docs: http://127.0.0.1:8000/docs

## Endpoint

POST /detect
- Content-Type: application/json
- Body: JSON with a single field `image` containing a base64-encoded image string (the server expects data URI style e.g. `"data:image/jpeg;base64,..."`).

Request example (Python):
```python
import base64, requests

url = "http://127.0.0.1:8000/detect"
with open("car.jpg", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")
payload = {"image": f"data:image/jpeg;base64,{b64}"}
resp = requests.post(url, json=payload)
print(resp.json())
```

Example cURL (small images; use caution with very large files):
```bash
# Convert image to base64 and send (Linux/macOS)
base64_img=$(base64 -w 0 car.jpg)
curl -X POST -H "Content-Type: application/json" \
  -d '{"image":"data:image/jpeg;base64,'"$base64_img"'"}' \
  http://127.0.0.1:8000/detect
```

Response (example):
```json
{
  "processed_image_base64": "data:image/jpeg;base64,...",
  "plates": ["ABC1234", "XYZ-987"]
}
```

- `processed_image_base64` can be rendered in a browser, written to disk after decoding, or shown in a UI.
- `plates` is a list of OCR results extracted from detected regions.

## Notes & Troubleshooting

- Model file not found or loading error:
  - Ensure `yolov8n.pt` is present or update path in `main.py`. If you trained a custom model, point to the trained `.pt`.
- OpenCV errors (imdecode failures):
  - Make sure `opencv-python-headless` (or `opencv-python`) is installed and compatible with your environment.
- EasyOCR performance:
  - EasyOCR uses PyTorch; installing the appropriate CUDA `torch` build significantly speeds up OCR and YOLO inference if you have a GPU.
- Torch/CUDA:
  - If you want GPU acceleration, install PyTorch with CUDA support matching your GPU driver.
  - See https://pytorch.org/get-started/locally/ for the correct install commands.
- Image size:
  - Very large images will increase inference time and memory usage. Consider resizing before sending to the API if necessary.
- CORS:
  - CORS is wide-open for testing. For production, restrict allowed origins.

## Potential Improvements
- Add authentication or rate-limiting for a production service.
- Return bounding box coordinates in the API response for client-side overlays.
- Improve OCR accuracy by pre-processing crops (deskew, contrast, denoising) and/or using a plate-specific OCR model.

## License & Attribution
- This repository uses:
  - YOLO / Ultralytics (https://github.com/ultralytics/ultralytics)
  - EasyOCR (https://github.com/JaidedAI/EasyOCR)
- Include the appropriate licenses for any models or code you reuse.
- This README and code are provided as-is.
