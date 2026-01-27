from fastapi import FastAPI, Request
import base64
import httpx

app = FastAPI()

LLAVA_URL = "http://83.96.121.186/api/chat"

@app.get("/health_check")
async def health_check():
    return {"status": "ok"}

@app.post("/image")
async def receive_image(request: Request):
    print("receiving image")

    body = await request.body()
    img_b64 = base64.b64encode(body).decode()

    payload = {
        "model": "llava",
        "messages": [
            {
                "role": "user",
                "content": "Describe what you see",
                "images": [img_b64]
            }
        ],
        "stream": False
    }

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(LLAVA_URL, json=payload)

    return r.json()

@app.get("/image")
async def image_check():
    return {"status": "ok"}