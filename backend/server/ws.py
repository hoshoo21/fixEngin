from typing import List
from fastapi import WebSocket

connected_clients: List[WebSocket] = []


async def broadcast_execution_report(report: dict):
    """Send execution reports to all connected websocket clients."""
    dead_clients = []

    for client in connected_clients:
        try:
            await client.send_json(report)
        except Exception:
            # client disconnected
            dead_clients.append(client)

    # cleanup
    for client in dead_clients:
        connected_clients.remove(client)
