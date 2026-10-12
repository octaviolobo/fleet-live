from fastapi import FastAPI, WebSocket , WebSocketDisconnect
import simulador 
from contextlib import asynccontextmanager
import asyncio

class ConnectionManager:
    def __init__(self):
        self.connections = []
    async def connect(self,websocket):
        await websocket.accept()
        self.connections.append(websocket)
    def disconnect(self,websocket):
        self.connections.remove(websocket)
    async def broadcast(self,data):
        for connection in self.connections.copy():
            try:
                await connection.send_json(data)
            except Exception:
                self.disconnect(connection)
manager = ConnectionManager()

async def broadcast_fleet():
    while True:
        await manager.broadcast(simulador.fleet_snapshot())
        await asyncio.sleep(1)
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    
    tasks = []
    #snapshot of the whole fleet one time
    tasks.append(asyncio.create_task(broadcast_fleet()))
    #load the trucks
    for t in simulador.TRUCKS:       
        tasks.append( asyncio.create_task(simulador.simulate_truck_movement(t)))
    yield
    #clear the trucks when applications stops 
    for c in tasks:
        c.cancel()
app = FastAPI(lifespan=lifespan)
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def truck_json():
    return simulador.fleet_snapshot()

@app.websocket("/ws/fleet")
async def truckinfo(websocket:WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)