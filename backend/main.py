from fastapi import FastAPI, WebSocket   
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
        for connection in self.connections:
            await connection.send_json(data)
manager = ConnectionManager()
@asynccontextmanager
async def lifespan(app: FastAPI):
    #load the trucks
    tasks = []
    for t in simulador.TRUCKS:
        Task = asyncio.create_task(simulador.simulate_truck_movement(t))
        tasks.append(Task)
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
    while True:
        await websocket.receive_text()