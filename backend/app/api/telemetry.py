import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.core.database import async_session_maker
from app.models.agent import Agent

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


class TelemetryBroadcast:
    def __init__(self):
        self.connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, message: dict):
        for conn in self.connections:
            try:
                await conn.send_json(message)
            except Exception:
                pass


broadcast = TelemetryBroadcast()


@router.websocket("/live")
async def telemetry_live(websocket: WebSocket):
    await broadcast.connect(websocket)
    try:
        async with async_session_maker() as db:
            result = await db.execute(select(Agent).order_by(Agent.id))
            agents = result.scalars().all()
            await websocket.send_json({
                "type": "snapshot",
                "agents": [
                    {
                        "id": a.id,
                        "name": a.name,
                        "module_type": a.module_type,
                        "status": a.status.value,
                        "last_heartbeat": a.last_heartbeat.isoformat() if a.last_heartbeat else None,
                    }
                    for a in agents
                ],
            })
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        broadcast.disconnect(websocket)
