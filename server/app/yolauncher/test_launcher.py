import pytest
from fastapi.testclient import TestClient
from server.app.yolauncher.models.package_models import get_packages
from .routers import router
from server.app.yolauncher.helpers.serialized_helper import package_list

client = TestClient(router)


# def test_create_package():
#     response = client.post(
#         "/create",
#         json={"package_name": "foobar", "type": "Foo Bar", "is_installed": True},
#     )
#     assert response.status_code == 201
#     res = {
#         'msg': "package created successfully",
#         'status': 201,
#         'data': []
#
#     }
#     assert response.json() == res

@pytest.mark.asyncio
async def test_get_all_package():
    response = client.get('/')
    assert response.status_code == 200
    datas = await get_packages()
    serialized_data = package_list(datas)

    res = {
        'msg': 'package get successfully',
        'status': 200,
        'pin': 2580,
        'all_apk': 'yo-launcher-apk/all_apk.zip',
        'data': serialized_data,
    }
    assert response.json() == res
