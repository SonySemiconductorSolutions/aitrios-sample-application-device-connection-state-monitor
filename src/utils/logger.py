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

import logging


def get_logger(name="device_connection_state_monitor"):
    logger = logging.getLogger(name)

    if not logger.hasHandlers():
        log_format = "%(asctime)s.%(msecs)-3d %(levelname)s %(message)s"
        date_format = "%Y-%m-%dT%H:%M:%S"
        formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
