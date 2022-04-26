from typing import List
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.key = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await websocket.send_json({"command": "connected", "value": "1"})

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    def active_connection(self):
        return self.active_connections

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        for connection in self.active_connections:
            if connection != websocket:
                await connection.send_json(message)

    async def send_message_on_specific_connection(
            self,
            message: dict,
            device_id: str,
            business_id: str,
            websocket: WebSocket
    ):
        is_available = False
        for connection in self.active_connections:
            if "device_id" in connection.query_params.keys() and "business_id" in connection.query_params.keys():
                connected_device = connection.query_params['device_id']
                connected_business = connection.query_params['business_id']
                if device_id == str(connected_device) and business_id == str(connected_business):
                    is_available = True
                    await connection.send_json(message)
        if not is_available:
            response = {
                'status': 'failed',
                'message': f'device with id {device_id} not connected'
            }
            await self.message_return_to_sender(response, websocket)

    async def send_msg_to_all_devices_under_business(self, message: dict, business_id: str):
        for connection in self.active_connections:
            if "business_id" in connection.query_params.keys():
                connected_business = connection.query_params['business_id']
                if business_id == str(connected_business):
                    await connection.send_json(message)

    async def send_response_to_admin(self, message: dict, websocket: WebSocket):
        ref_id = websocket.query_params["device_id"]
        message['ref_device'] = ref_id
        for connection in self.active_connections:
            if connection.query_params["device_id"] == 'admin_device':
                await connection.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except ConnectionError:
                print('connection error')

    async def message_return_to_sender(self, msg: dict, websocket: WebSocket):
        try:
            await websocket.send_json(msg)
        except ConnectionError:
            print('connection error')


manager = ConnectionManager()
