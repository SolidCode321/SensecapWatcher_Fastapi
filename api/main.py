from fastapi import FastAPI

app = FastAPI()

LLAVA_URL = "http://83.96.121.186/api/chat"

@app.get("/health_check")
async def health_check():
    return {"status": "ok"}

'''@app.post("/image")
async def receive_image(request: Request):
    print("recieving image")
    body = await request.body()

    # If Watcher sends raw JPEG
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

    r = requests.post(LLAVA_URL, json=payload)
    return r.json()

@app.get("/image")
async def receive_chat(request: Request):
    return {"status": "ok"}'''

