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

from ..depend.find_codec import find_codec


def get_text(fnm: str, binary=None) -> str:
    txt = ""
    if binary:
        encoding = find_codec(binary)
        txt = binary.decode(encoding, errors="ignore")
    else:
        # 先尝试UTF-8
        try:
            with open(fnm, "r", encoding="utf-8") as f:
                txt = f.read()
        except UnicodeDecodeError:
            # 如果UTF-8失败，使用find_codec检测编码
            with open(fnm, "rb") as f:
                binary_content = f.read()
            encoding = find_codec(binary_content)
            txt = binary_content.decode(encoding, errors="ignore")
    return txt
