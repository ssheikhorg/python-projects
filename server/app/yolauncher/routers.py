import os
import shutil
from fastapi import UploadFile, File, Form, WebSocket, APIRouter
from starlette import status
import pathlib
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.websockets import WebSocketDisconnect
from server.app.yolauncher.helpers.serialized_helper import return_response
from server.app.yolauncher.helpers.utils import socket_command_handler, handle_get_packages
from server.app.yolauncher.models.business_models import BusinessModel, business_create, added_new_package_all_business
from server.app.yolauncher.models.package_models import PackageModel, \
    package_create, package_get_by_id, upload_file
from server.app.yolauncher.helpers.socket_manager import manager

router = APIRouter()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Command</title>
    </head>
    <body>
        <h1>WebSocket Command to App</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="command" placeholder="command" autocomplete="off"/>
            <input type="text" id="package_id" placeholder="package name/ id" autocomplete="off"/>
            <input type="text" id="device_id" placeholder="Device Id" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new 
            WebSocket("wss://905a-103-113-175-2.ngrok.io/launcher/websocket?device_id=5646544947&business_id=0101101010");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var command = document.getElementById("command").value
                var package_id = document.getElementById("package_id").value
                var device_id = document.getElementById("device_id").value
                value = {
                    "command": command,
                    "value": package_id,
                    "device_id": device_id,
                }
                ws.send(JSON.stringify(value))  
                command.value = ''
                package_id.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@router.get('/websocket-connection')
async def connect_socket_ui():
    return HTMLResponse(html)


@router.websocket('/websocket')
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await socket_command_handler(data, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.get('/')
async def get_all_package(request: Request):
    if 'device_id' in request.headers:
        print(request.headers['device_id'])
        datas = await handle_get_packages(request.headers['device_id'])
        if len(datas) > 0:
            response = {
                'msg': 'package get successfully',
                'status': status.HTTP_200_OK,
                'data': datas,
            }
            return JSONResponse(status_code=status.HTTP_200_OK, content=response)
        response = {
            'msg': 'No Package Found',
            'status': status.HTTP_404_NOT_FOUND,
            'data': [],
        }
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=response)
    else:
        response = return_response('device_id missing in header parameter', status.HTTP_422_UNPROCESSABLE_ENTITY)
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=response)


@router.post('/create')
async def create_package(package: PackageModel):
    insert_obj = await package_create(package)
    await added_new_package_all_business(package, insert_obj['package_id'])
    if insert_obj['insert_obj'].inserted_id:
        response = {
            'msg': 'package created successfully',
            'status': status.HTTP_201_CREATED,
        }
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=response)
    response = {
        'msg': 'package not created',
        'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response)


@router.post('/create/business')
async def create_business(business: BusinessModel):
    insert_obj = await business_create(business)
    if insert_obj:
        response = {
            'msg': 'Business created successfully',
            'status': status.HTTP_201_CREATED,
        }
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=response)
    response = {
        'msg': 'Business not created',
        'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response)


@router.post('/package')
async def get_package_by_id(package_id: str = Form(...)):
    package_by_id = await package_get_by_id(package_id)
    if package_by_id:
        data = {
            'package_name': package_by_id['package_name'],
            'package_id': package_by_id['package_id'],
            'apk_path': package_by_id['apk_path'],
            'type': package_by_id['type'],
            'created_at': package_by_id['created_at'],
        }
        response = {
            'msg': 'package get successfully',
            'status': status.HTTP_200_OK,
            'data': data,
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=response)
    response = {
        'msg': 'No package found with the given id',
        'status': status.HTTP_404_NOT_FOUND,
        'data': {},
    }
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=response)


@router.post("/apk-upload")
async def upload_apk(request: Request, package_id: str, file: UploadFile = File(...)):
    if request.method == "POST":
        package_by_id = await package_get_by_id(package_id)
        if package_by_id:
            if not os.path.exists('server/app/yolauncher/launcherfiles/'):
                os.makedirs('server/app/yolauncher/launcherfiles/')
            file_extension = pathlib.Path(file.filename).suffix
            if file_extension == '.apk':
                upload_path = 'server/app/yolauncher/launcherfiles/'
                upload_url = str(upload_path + package_id + '.apk')
                with open(upload_url, "wb") as apk:
                    shutil.copyfileobj(file.file, apk)
                path = 'yo-launcher-apk/'
                file_url = str(path + package_id + '.apk')
                response = {
                    'apk_path': file_url,
                }
                update_apk_path = await upload_file(package_id, response)
                if update_apk_path:
                    response = return_response('file uploaded successfully', status.HTTP_200_OK)
                    return JSONResponse(status_code=status.HTTP_201_CREATED, content=response)
            else:
                response = return_response('This is not a valid apk file', status.HTTP_406_NOT_ACCEPTABLE)
                return JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE, content=response)
        else:
            response = return_response('No package found with the given id', status.HTTP_404_NOT_FOUND)
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=response)

        response = {
            'apk_path': file_url,
        }
        update_apk_path = await upload_file(package_id, response)
        if update_apk_path:
            return {
                'msg': 'file uploaded successfully',
                'status': status.HTTP_200_OK,
            }
    raise HTTPException(status_code=405, detail=f"this request should on POST method")
