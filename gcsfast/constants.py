# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Program-wide constants.
"""

PROGRAM_ROOT_LOGGER_NAME = "gcsfast"
DEFAULT_MINIMUM_DOWNLOAD_SLICE_SIZE = 262144 * 4 * 64  # 64MiB
DEFAULT_MAXIMUM_DOWNLOAD_SLICE_SIZE = 262144 * 4 * 1024  # 1GiB