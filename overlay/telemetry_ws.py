import asyncio
import socketio
from telemetry_pipeline import get_live_telemetry

sio = socketio.AsyncServer(cors_allowed_origins='*')
app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

async def telemetry_loop():
    while True:
        data = get_live_telemetry()  # {'fps': 122, 'gpu_temp': 72, ...}
        await sio.emit('telemetry', data)
        await asyncio.sleep(1 / 30)

if __name__ == '__main__':
    import uvicorn
    loop = asyncio.get_event_loop()
    loop.create_task(telemetry_loop())
    uvicorn.run(app, host='0.0.0.0', port=8502)
