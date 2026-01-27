from fastapi import FastAPI, Request, HTTPException
import base64
import requests

app = FastAPI()

LLAVA_URL = "http://83.96.121.186/api/chat"

# Basic Auth credentials
USERNAME = "Alessa"
PASSWORD = "Alessa@123"

@app.get("/health_check")
def health_check():
    return {"status": "ok"}

@app.post("/image")
async def receive_image(request: Request):
    try:
        # Receive raw JPEG
        body = await request.body()

        if not body:
            raise HTTPException(status_code=400, detail="Empty image")

        # Convert to base64 (NO data:image/... prefix)
        img_b64 = base64.b64encode(body).decode("utf-8")

        payload = {
            "model": "llava",
            "messages": [
                {
                    "role": "user",
                    "content": "Do you see a black cat in this image?",
                    "images": [img_b64]
                }
            ],
            "stream": False
        }

        headers = {
            "Content-Type": "application/json"
        }

        # requests supports basic auth natively
        response = requests.post(
            LLAVA_URL,
            json=payload,
            headers=headers,
            auth=(USERNAME, PASSWORD),
            timeout=60
        )

        # Raise if LLaVA returns 4xx/5xx
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.get("/image")
def image_check():
    return {"status": "ok"}