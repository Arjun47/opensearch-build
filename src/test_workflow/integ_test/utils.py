# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import base64
import semver


def get_password(version: str, convert_to_base64: bool = False) -> str:
    # Starting in 2.12.0, demo configuration setup script requires a strong password
    to_base64 = lambda p: base64.b64encode(p).encode("utf-8").decode("utf-8")
    if semver.compare(version, '2.12.0') != -1:
        return to_base64("myStrongPassword123!") if convert_to_base64 else "myStrongPassword123!"
    else:
        return to_base64("admin") if convert_to_base64 else "admin"
