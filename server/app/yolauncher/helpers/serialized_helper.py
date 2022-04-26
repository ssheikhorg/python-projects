def convert_list_with_dict(item) -> dict:
    return {
        'package_name': item['package_name'],
        'package_id': item['package_id'],
        'apk_path': item['apk_path'],
        'type': item['type'],
    }


def convert_private_list(item) -> dict:
    return {
        'package_name': item['device_info']['packages']['package_name'],
        'package_id': item['device_info']['packages']['package_id'],
        'apk_path': item['device_info']['packages']['apk_path'],
        'type': item['device_info']['packages']['type'],
    }


def package_list(entity) -> list:
    if len(entity) == 0:
        return []
    else:
        li = [convert_list_with_dict(item) for item in entity]
        return li


def private_package_list(entity) -> list:
    if len(entity) == 0:
        return []
    else:
        li = [convert_private_list(item) for item in entity]
        return li


def return_response(msg: str, status: int, data=None):
    if data is None:
        data = []
    return {
        'msg': msg,
        'status': status,
        'data': data
    }
