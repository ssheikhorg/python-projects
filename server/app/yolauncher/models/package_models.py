import datetime
import uuid

from pydantic import BaseModel
from server.app.database.db import package_collection


class PackageModel(BaseModel):
    package_name: str
    status: bool = True
    type: str
    is_installed: bool = True
    apk_path: str = ''

    class Config:
        orm_mode = True


class FailedPackage(BaseModel):
    packages: list
    device_id: str


async def get_packages():
    pipeline = [
        {'$match': {"status": True}},
        {
            '$project':
                {
                    '_id': 0,
                    'package_name': 1,
                    'package_id': 1,
                    'apk_path': 1,
                    'type': 1,
                    'is_installed': 1
                }
        }

    ]
    all_packages = package_collection.aggregate(pipeline)
    if all_packages:
        datas = list(all_packages)
        return datas
    return []


async def package_create(package):
    package_id = uuid.uuid4().hex
    data = {
        'package_name': package.package_name,
        'package_id': package_id,
        'apk_path': package.apk_path,
        'type': package.type,
        'created_at': str(datetime.date.today()),
        'status': package.status,
        'is_installed': package.is_installed
    }

    insert_obj = package_collection.insert_one(data)
    response = {
        "insert_obj": insert_obj,
        "package_id": package_id
    }
    return response


async def package_update(package, data):
    package_collection.update_one(
        {'package_id': package},
        {'$set': data}
    )
    return True


async def package_get_by_id(package_id):
    package = package_collection.find_one({'package_id': package_id})
    return package


async def package_get_by_name(package_name):
    package = package_collection.find_one({'package_name': package_name})
    return package


async def upload_file(package_id, response):
    upload = package_collection.update_one({'package_id': package_id}, {'$set': response})
    return upload
