import asyncio
import random
import socketio
from fastapi import FastAPI
from threading import Thread
import GPUtil

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = FastAPI()
asgi_app = socketio.ASGIApp(sio, other_asgi_app=app)

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

async def emit_telemetry():
    while True:
        gpus = GPUtil.getGPUs()
        if not gpus:
            continue
        gpu = gpus[0]
        data = {
            "fps": random.randint(120, 240),  # Replace with real FPS capture
            "temp": round(gpu.temperature, 1),
            "load": int(gpu.load * 100),
            "vram": round(gpu.memoryUsed / 1024, 2)  # GB
        }
        await sio.emit("telemetry", data)
        await asyncio.sleep(0.5)  # 2 FPS updates/sec

def start_server():
    import uvicorn
    uvicorn.run(asgi_app, host="0.0.0.0", port=8000)

def run_telemetry_loop():
    asyncio.run(emit_telemetry())

if __name__ == "__main__":
    Thread(target=start_server).start()
    run_telemetry_loop()
