from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import requests
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ---------------- CONFIG ----------------
LLAVA_URL = "http://83.96.121.186/api/chat"
USERNAME = "Alessa"
PASSWORD = "Alessa@123"

# Prompt is now mutable
current_prompt = {
    "text": "Answer YES or NO only. Do you see a black cat in this image?"
}

detections = []
MAX_DETECTIONS = 50
# ----------------------------------------


@app.get("/health_check")
def health_check():
    return {"status": "ok"}


# ---------- Prompt API ----------
@app.get("/api/prompt")
def get_prompt():
    return {"prompt": current_prompt["text"]}


@app.post("/api/prompt")
async def set_prompt(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "").strip()

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    current_prompt["text"] = prompt
    return {"status": "ok", "prompt": prompt}


# ---------- SenseCAP webhook ----------
@app.post("/image")
async def receive_image(request: Request):
    try:
        payload = await request.json()

        events = payload.get("events")
        if not events or "img" not in events:
            raise HTTPException(status_code=400, detail="Invalid SenseCAP packet")

        img_b64 = events["img"]
        device_eui = payload.get("deviceEui", "unknown")

        llava_payload = {
            "model": "llava",
            "messages": [
                {
                    "role": "user",
                    "content": current_prompt["text"],
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

        detections.insert(0, {
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "device": device_eui,
            "prompt": current_prompt["text"],
            "image": img_b64,
            "response": ai_text
        })

        del detections[MAX_DETECTIONS:]

        return {"status": "ok"}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Detections API ----------
@app.get("/api/detections")
def get_detections():
    return JSONResponse(detections)


# ---------- Dashboard ----------
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})