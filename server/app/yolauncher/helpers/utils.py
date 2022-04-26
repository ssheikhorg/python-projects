from server.app.yolauncher.helpers.serialized_helper import private_package_list, package_list
from server.app.yolauncher.helpers.socket_manager import manager
from server.app.yolauncher.models.business_models import private_package_update, \
    get_package_based_on_business, get_private_packages, get_business_by_id, update_business_pin_by_id
from server.app.yolauncher.models.package_models import get_packages

command_types = {
        'install_app': 'apk path to download apk',
        'uninstall': 'package name',
        'change_wallpaper': 'change wallpaper',
        'update': 'apk path to download apk',
        'change_pin': '4 digit number',
        'remove_from_lock_app': 'package name',
        'remove_from_launcher': 'package name',
        'remove_from_both_app': 'package name',
        'add_to_both_app': 'package name',
        'add_to_launcher': 'package name',
        'add_to_lock_app': 'package name',
        'reboot': '',
        'response_back': 'message'

}

data_modifier_command = [
    'add_to_both_app',
    'add_to_launcher',
    'add_to_lock_app',
    'remove_from_lock_app',
    'remove_from_launcher',
    'remove_from_both_app',
    'response_back',
]

command_keys = {
    'command': 'instructions that should execute *',
    'value': 'instructions type value (package_id/package_name) *',
    'device_id': 'from which device socket request come',
    'business_id': 'which business it should update',
}


async def socket_command_handler(data, websocket):
    if ('command' in data and data['command'] != '') and 'value' in data:
        is_validate = is_socket_command_validate(data['command'])
        if is_validate:
            if data['command'] == 'change_pin':
                await handle_change_pin(data, websocket)
                return
            if data['command'] in data_modifier_command:
                await handle_commands(data, websocket)
            else:
                await send_response(data, websocket)
        else:
            response = {
                'status': 'failed',
                'message': 'invalid command',
                'accepted_type': command_types
            }
            await manager.message_return_to_sender(response, websocket)
    else:
        response = {
            'status': 'failed',
            'message': 'invalid key in json',
            'accepted_type': command_keys
        }
        await manager.message_return_to_sender(response, websocket)


def is_socket_command_validate(command):
    if command not in command_types.keys():
        return False
    else:
        return True


async def handle_change_pin(data, websocket):
    if data['value'] != '' and data['business_id'] != '':
        get_business = await get_business_by_id(data['business_id'])
        if len(get_business) > 0:
            await update_business_pin_by_id(data['business_id'], data['value'])
            await manager.send_msg_to_all_devices_under_business(data, data['business_id'])
        else:
            response = {
                'status': 'failed',
                'message': 'business not found with this business id'
            }
            await manager.message_return_to_sender(response, websocket)
    else:
        response = {
            'status': 'failed',
            'message': 'value & business id cannot be empty'
        }
        await manager.message_return_to_sender(response, websocket)


async def handle_commands(data, websocket):
    package = await get_package_based_on_business(data['value'], data['business_id'], data['device_id'])
    if len(package) > 0:
        match_package = package[0]
        package_type = match_package['device_info']['packages']['type']
        match data['command']:
            case 'add_to_both_app':
                if package_type != 'both':
                    updated_schema = {
                        'type': 'both'
                    }
                    await private_package_update(data['value'], data['business_id'], data['device_id'], updated_schema)
                    await send_response(data, websocket)
                else:
                    response = {
                        'status': 'failed',
                        'message': 'this package has already added as both app',
                    }
                    await manager.message_return_to_sender(response, websocket)

            case 'add_to_launcher':
                if package_type == 'locker_apps' or package_type == 'both' or package_type == "":
                    if package_type == "":
                        updated_schema = {
                            'type': 'launcher_apps'
                        }
                    else:
                        updated_schema = {
                            'type': 'both'
                        }
                    await private_package_update(data['value'], data['business_id'], data['device_id'], updated_schema)
                    await send_response(data, websocket)
                else:
                    response = {
                        'status': 'failed',
                        'message': f"this package has already added as {package['type']} app",
                    }
                    await manager.message_return_to_sender(response, websocket)

            case 'add_to_lock_app':
                if package_type == 'launcher_apps' or package_type == 'both' or package_type == "":
                    if package_type == "":
                        updated_schema = {
                            'type': 'locker_apps'
                        }
                    else:
                        updated_schema = {
                            'type': 'both'
                        }
                    await private_package_update(data['value'], data['business_id'], data['device_id'], updated_schema)
                    await send_response(data, websocket)
                else:
                    response = {
                        'status': 'failed',
                        'message': f"this package has already added as {package['type']} app",
                    }
                    await manager.message_return_to_sender(response, websocket)

            case 'remove_from_lock_app':
                if package_type == 'both' or package_type == 'locker_apps':
                    if package_type == "both":
                        updated_schema = {
                            'type': 'launcher_apps'
                        }
                    else:
                        updated_schema = {
                            'type': ''
                        }
                    await private_package_update(data['value'], data['business_id'], data['device_id'], updated_schema)
                    await send_response(data, websocket)
                else:
                    response = {
                        'status': 'failed',
                        'message': f"this package has already added as {package['type']} app",
                    }
                    await manager.message_return_to_sender(response, websocket)

            case 'remove_from_launcher':
                if package_type == 'both' or package_type == 'launcher_apps':
                    if package_type == "both":
                        updated_schema = {
                            'type': 'locker_apps'
                        }
                    else:
                        updated_schema = {
                            'type': ''
                        }
                    await private_package_update(data['value'], data['business_id'], data['device_id'], updated_schema)
                    await send_response(data, websocket)
                else:
                    response = {
                        'status': 'failed',
                        'message': f"this package has already added as {package['type']} app",
                    }
                    await manager.message_return_to_sender(response, websocket)

            case 'remove_from_both_app':
                if package_type != '':
                    updated_schema = {
                        'type': ''
                    }
                    await private_package_update(data['value'], data['business_id'], data['device_id'], updated_schema)
                    await send_response(data, websocket)
                else:
                    response = {
                        'status': 'failed',
                        'message': f"this package has already remove from both app",
                    }
                    await manager.message_return_to_sender(response, websocket)

            case 'response_back':
                await manager.send_response_to_admin(data, websocket)
            case _:
                pass
    else:
        response = {
            'status': 'failed',
            'message': f"package not found",
        }
        await manager.message_return_to_sender(response, websocket)


async def send_response(data, websocket):
    print(data)
    device_key = "device_id"
    business_key = "business_id"
    if device_key in data and business_key in data:
        if data['device_id'] != "" and data['business_id'] != "":
            await manager.send_message_on_specific_connection(data, data["device_id"], data["business_id"], websocket)
        if data['device_id'] == "" and data['business_id'] != "":
            await manager.send_msg_to_all_devices_under_business(data, data['business_id'])
        if data['device_id'] == "" and data['business_id'] == "":
            await manager.send_personal_message(data, websocket)
    else:
        response = {
            'status': 'failed',
            'message': 'missing key device_id and business_id, you can send empty string of those keys'
        }
        await manager.message_return_to_sender(response, websocket)


async def handle_get_packages(device_id, business_id=''):
    if device_id != '' and business_id == '':
        packages = await get_private_packages(device_id, business_id)
        if len(packages) > 0:
            serialized_package = private_package_list(packages)
            return serialized_package
        else:
            datas = await get_packages()
            if len(datas) > 0:
                serialized_data = package_list(datas)
                return serialized_data
            else:
                return []
    else:
        datas = await get_packages()
        if len(datas) > 0:
            serialized_data = package_list(datas)
            return serialized_data
        else:
            return []
