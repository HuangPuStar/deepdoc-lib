#
#  Copyright 2025 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import logging
import os

logger = logging.getLogger(__name__)


def pip_install_torch():
    """
    Install torch based on system configuration.
    This is a simplified version for the independent library.
    """
    try:
        import torch

        logger.info("PyTorch is already installed")
        return True
    except ImportError:
        return False


def parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def offline_mode_or_from_env(offline: bool | None = None) -> bool:
    return offline if offline is not None else parse_bool(os.getenv("DEEPDOC_OFFLINE"), default=False)
