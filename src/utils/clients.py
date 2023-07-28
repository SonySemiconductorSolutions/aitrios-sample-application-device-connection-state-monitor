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

import importlib
import json
import requests
import sys
from console_access_library.client import Client
from console_access_library.common.config import Config
from config import config
from utils.logger import get_logger


logger = get_logger()


def get_console_client():
    """Get access information from setting file and generate ConsoleAccessClient.
    Returns:
        ConsoleAccessClient: ConsoleAccessClient instance generated from access information.
    """

    settings = _get_settings()

    config_obj = Config(
        settings.console_access_settings["console_endpoint"],
        settings.console_access_settings["portal_authorization_endpoint"],
        settings.console_access_settings["client_id"],
        settings.console_access_settings["client_secret"]
    )
    client_obj = Client(config_obj)

    return client_obj


def notify_by_slack(message):
    """Send notification by Slack api.
    Args:
        message (str): Message to send
    """

    settings = _get_settings()
    if not hasattr(settings, "slack_settings"):
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + settings.slack_settings["access_token"],
    }
    data = {
        "channel": settings.slack_settings["channel"],
        "text": "<!channel>\n" + message,
    }
    _post_request("https://slack.com/api/chat.postMessage", headers=headers, data=data)


def notify_by_sendgrid(message):
    """Send notification by SendGrid api.
    Args:
        message (str): Message to send
    """

    settings = _get_settings()
    if not hasattr(settings, "sendgrid_settings"):
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + settings.sendgrid_settings["apikey"],
    }
    data = {
        "personalizations": [{
            "to": [{"email": mail} for mail in settings.sendgrid_settings["mail_to"]]
        }],
        "from": {"email": settings.sendgrid_settings["mail_from"]},
        "subject": config.EMAIL_SUBJECT,
        "content": [{
            "type": "text/plain",
            "value": message
        }]
    }
    _post_request("https://api.sendgrid.com/v3/mail/send", headers=headers, data=data)


def _post_request(url, headers, data):
    try:
        res = requests.post(url, headers=headers, data=json.dumps(data))
        res.raise_for_status()
    except Exception:
        logger.exception("Failed to notify message.")


def _get_settings():
    global _settings

    if _settings is None:
        if importlib.util.find_spec("config.access_settings"):
            _settings = importlib.import_module("config.access_settings")
        else:
            logger.error(
                "src/config/access_settings.py is not exists. "
                "Rename access_settings.py.sample to access_settings.py and set credentials.")
            sys.exit(1)

    return _settings


_settings = None
