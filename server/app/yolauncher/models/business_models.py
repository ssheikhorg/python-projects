import uuid
import datetime
from pydantic import BaseModel
from server.app.database.db import business_collection
from server.app.yolauncher.models.package_models import get_packages


class BusinessModel(BaseModel):
    device_id: str
    device_name: str = ''
    business_id: str
    pin: str = ''
    business_name: str = ''
    failed_packages: list = []

    class Config:
        orm_mode = True


async def business_create(business):
    b_id = uuid.uuid4().hex
    is_business_available = business_collection.find_one({'business_id': business.business_id})
    get_public_package = await get_packages()

    response = {
        'device_id': business.device_id,
        'device_name': business.device_name,
        'packages': get_public_package
    }
    if is_business_available:
        insert_obj = business_collection.update_one(
            {
                "business_id": business.business_id,
                "device_info.device_id": {
                    "$ne": business.device_id
                }
            },
            {"$push": {"device_info": response}},
        )
        if len(business.failed_packages) > 0:
            await packages_update(business.failed_packages, business.business_id, business.device_id)
        return insert_obj
    else:
        device_info_list = [response]
        data = {
            'id': b_id,
            'device_info': device_info_list,
            'business_id': business.business_id,
            'business_name': business.business_name,
            'pin': business.pin,
            'created_at': str(datetime.date.today()),
        }

        insert_obj = business_collection.insert_one(data)
        if len(business.failed_packages) > 0:
            await packages_update(business.failed_packages, business.business_id, business.device_id)
        return insert_obj


async def packages_update(packages, business_id, device_id):
    ack = []
    for package in packages:
        update = business_collection.update_one(
            {
                "business_id": business_id,
                "device_info": {
                    "$elemMatch": {
                        "device_id": device_id,
                        "packages.package_id": package
                    }
                }
            },
            {
                "$set": {"device_info.$[outer].packages.$[inner].is_installed": False}
            },
            array_filters=[
                {"outer.device_id": device_id},
                {"inner.package_id": package}],
            upsert=True
        )
        if update.raw_result['updatedExisting']:
            ack.append('updated')
        else:
            ack.append('not updated')
    return ack


async def private_package_update(package_name, business_id, device_id, updated_schema):
    key_name = [key for key in updated_schema.keys()][0]
    update = business_collection.update_one(
        {
            "business_id": business_id,
            "device_info": {
                "$elemMatch": {
                    "device_id": device_id,
                    "packages.package_name": package_name
                }
            }
        },
        {
            "$set": {f"device_info.$[outer].packages.$[inner].{key_name}": updated_schema[key_name]}
        },
        array_filters=[
            {"outer.device_id": device_id},
            {"inner.package_name": package_name}],
        upsert=True
    )
    return update.raw_result['updatedExisting']


async def get_package_based_on_business(package_name, business_id, device_id):
    pipline = [
        {"$match": {"business_id": business_id}},
        {"$unwind": "$device_info"},
        {"$match": {"device_info.device_id": device_id}},
        {"$unwind": "$device_info.packages"},
        {"$match": {"device_info.packages.package_name": package_name}},
        {
            "$project":
                {
                    'device_info.packages.type': 1,
                    '_id': 0
                }
        },

    ]
    result = business_collection.aggregate(pipline)
    return list(result)


async def get_private_packages(device_id, business_id=''):
    pipeline = [
        # {"$match": {"business_id": business_id}},
        {"$unwind": "$device_info"},
        {"$match": {"device_info.device_id": device_id}},
        {"$unwind": "$device_info.packages"},
        {
            "$project":
                {
                    'device_info.packages': 1,
                    '_id': 0
                }
        },
    ]
    packages = business_collection.aggregate(pipeline)
    if packages:
        package_list = list(packages)
        return package_list
    else:
        return []


async def added_new_package_all_business(package, package_id):
    cur = business_collection.find()
    if cur.count() != 0:
        data = {
            'package_name': package.package_name,
            'package_id': package_id,
            'apk_path': package.apk_path,
            'type': package.type,
            'created_at': str(datetime.date.today()),
            'status': package.status,
            'is_installed': package.is_installed
        }
        update = business_collection.update_many(
            {},
            {
                "$push": {
                    "device_info.$[].packages": data
                }
            },

        )
        return update
    else:
        return []


async def get_business_by_id(business_id):
    pipeline = [
        {'$match': {"business_id": business_id}},
        {
            '$project':
                {
                    '_id': 0,
                    'business_name': 1,
                    'pin': 1,
                }
        }

    ]
    all_packages = business_collection.aggregate(pipeline)
    if all_packages:
        datas = list(all_packages)
        return datas
    return []


async def update_business_pin_by_id(business_id, pin):
    updated_business = business_collection.update_one({"business_id": business_id}, {"$set": {"pin": pin}})
    return updated_business.raw_result['updatedExisting']
