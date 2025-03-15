import asyncio
import asyncpg
import os
import json  # Ensure this is imported at the top of the file
from fastapi import APIRouter, status, WebSocket, WebSocketDisconnect
from db_env import DB_CACHE_URL

router = APIRouter()


# WebSocket manager to handle connected clients
class WebSocketManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_to_user(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            try:
                # Convert the dictionary to a JSON string before sending
                await self.active_connections[user_id].send_text(json.dumps(message))
            except WebSocketDisconnect:
                self.disconnect(user_id)


websocket_manager = WebSocketManager()


# WebSocket endpoint with user identification
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket_manager.connect(websocket, user_id)
    try:
        # Fetch and send data specific to the connected user
        conn = await asyncpg.connect(DB_CACHE_URL)
        try:
            rows = await conn.fetch(
                "SELECT * FROM test_table WHERE rescuer_id = $1 AND done = false ORDER BY id ASC",
                user_id,
            )
            print(f"Initial rows for user_id {user_id}: {rows}")
            for row in rows:
                await websocket_manager.send_to_user(user_id, dict(row))
        finally:
            await conn.close()

        # Keep the connection alive and listen for messages
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(user_id)


# Listen for PostgreSQL notifications
async def listen_to_db():
    conn = await asyncpg.connect(DB_CACHE_URL)
    await conn.add_listener("realtime_updates", handle_notification)
    try:
        while True:
            await asyncio.sleep(1)  # Keep the connection alive
    finally:
        await conn.close()


# Handle PostgreSQL notifications
async def handle_notification(connection, pid, channel, payload):
    conn = await asyncpg.connect(DB_CACHE_URL)
    try:
        # Parse the payload as JSON if it contains JSON data
        try:
            payload_data = json.loads(payload)  # Convert payload to a dictionary
            user_id = payload_data.get("rescuer_id")  # Extract rescuer_id
        except json.JSONDecodeError:
            print(f"Payload is not valid JSON: {payload}")
            return

        if user_id in websocket_manager.active_connections:
            rows = await conn.fetch(
                "SELECT * FROM test_table WHERE rescuer_id = $1 AND done = false ORDER BY id ASC",
                user_id,
            )
            print(f"Rows for user_id {user_id}: {rows}")
            for row in rows:
                # Send the row data to the specific user
                await websocket_manager.send_to_user(user_id, dict(row))
    finally:
        await conn.close()


# Start the database listener on app startup
async def start_db_listener():
    asyncio.create_task(listen_to_db())
