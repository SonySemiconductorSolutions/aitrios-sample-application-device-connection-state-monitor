"""
Copyright 2023 Sony Semiconductor Solutions Corp. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from config import config
from utils import clients
from utils.logger import get_logger
from utils.time import sleep


logger = get_logger()


def main_loop():
    logger.info("Start monitoring.")

    console_client = clients.get_console_client()
    state_prev_cache = {}  # key=device_id, value=connectionState

    while True:
        try:
            res = console_client.device_management.get_devices()

            devices_connected, devices_disconnected = [], []

            for device_info in res["devices"]:
                device_id = device_info["device_id"]
                state_latest = device_info["connectionState"]
                state_prev = state_prev_cache.get(device_id)

                if state_prev == "Disconnected" and state_latest == "Connected":
                    devices_connected.append(device_info)
                elif state_prev == "Connected" and state_latest == "Disconnected":
                    devices_disconnected.append(device_info)

                state_prev_cache[device_id] = state_latest

            if devices_connected or devices_disconnected:
                send_notification(devices_connected, devices_disconnected)

        except Exception:
            logger.exception("Failed to get devices.")

        sleep(config.INTERVAL_MIN * 60)


def send_notification(devices_connected, devices_disconnected):
    """Create message and send notification.
    Args:
        devices_connected (list): List of connected devices
        devices_disconnected (list): List of disconnected devices
    """

    def _create_devicelist_str(device_info_list):
        devices = []
        for device_info in device_info_list:
            devices.append("- %s  %s (lastActivityTime: %s)" % (
                device_info.get("device_id", "-"),
                device_info.get("property", {}).get("device_name", "-"),
                device_info.get("lastActivityTime", "-")))

        return "\n".join(sorted(devices))

    msg_list = []
    if devices_connected:
        msg_list.append("*** Following device connected ***\n"
                        + _create_devicelist_str(devices_connected))
    if devices_disconnected:
        msg_list.append("!!! Following device disconnected !!!\n"
                        + _create_devicelist_str(devices_disconnected))

    message = "\n\n".join(msg_list)

    logger.info(message)

    clients.notify_by_slack(message)
    clients.notify_by_sendgrid(message)


if __name__ == "__main__":
    main_loop()
