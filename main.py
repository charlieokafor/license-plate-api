from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import cv2
import numpy as np
import easyocr
from ultralytics import YOLO
import io

app = FastAPI()

# Allow all origins (for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models
model = YOLO("yolov8n.pt")  # Replace with your custom license plate model
reader = easyocr.Reader(["en"])

class ImageInput(BaseModel):
    image: str  # base64 encoded string

@app.post("/detect")
async def detect_plate(data: ImageInput):
    try:
        # Decode base64
        header, encoded = data.image.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Run YOLO
        results = model(frame)[0]

        plate_texts = []
        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            cropped = frame[y1:y2, x1:x2]

            # OCR
            ocr_result = reader.readtext(cropped)
            text = " ".join([i[1] for i in ocr_result])
            if text:
                plate_texts.append(text)

            # Draw box and label
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)

        # Encode final image as base64
        _, buffer = cv2.imencode(".jpg", frame)
        base64_img = base64.b64encode(buffer).decode("utf-8")
        base64_img = f"data:image/jpeg;base64,{base64_img}"

        return {
            "processed_image_base64": base64_img,
            "plates": plate_texts
        }

    except Exception as e:
        return {"error": str(e)}
