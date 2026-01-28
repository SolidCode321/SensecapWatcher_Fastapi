from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

LLAVA_URL = "http://83.96.121.186/api/chat"

USERNAME = "Alessa"
PASSWORD = "Alessa@123"

# ---- In-memory store (simple & effective) ----
detections = []

PROMPT = "Do you see a person wearing an orange sweater in this image?"

@app.get("/health_check")
def health_check():
    return {"status": "ok"}

@app.post("/image")
async def receive_image(request: Request):
    try:
        payload_in = await request.json()

        events = payload_in.get("events")
        if not events or "img" not in events:
            raise HTTPException(status_code=400, detail="Invalid packet")

        img_b64 = events["img"]
        device_eui = payload_in.get("deviceEui", "unknown")

        llava_payload = {
            "model": "llava",
            "messages": [
                {
                    "role": "user",
                    "content": PROMPT,
                    "images": [img_b64]
                }
            ],
            "stream": False
        }

        response = requests.post(
            LLAVA_URL,
            json=llava_payload,
            auth=(USERNAME, PASSWORD),
            timeout=60
        )
        response.raise_for_status()
        llava_response = response.json()

        ai_text = (
            llava_response
            .get("message", {})
            .get("content", "")
        )

        # ---- Save result for dashboard ----
        detections.insert(0, {
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "device": device_eui,
            "prompt": PROMPT,
            "image": img_b64,
            "response": ai_text
        })

        # Keep last 50 only
        detections[:] = detections[:50]

        return {"status": "ok"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Dashboard ----
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "detections": detections
        }
    )