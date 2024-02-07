# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import logging
from typing import Any

from validation_workflow.api_request import ApiTest

'''
This class is the collection of test cases to run.
'''


class ApiTestCases:

    def __init__(self) -> None:
        pass

    @staticmethod
    def test_apis(version: str, projects: list, security_plugin_exists: bool = True) -> Any:
        pass_counter, fail_counter = 0, 0

        test_apis = [
            ['https://localhost:9200/', 200, ''],
            ['https://localhost:9200/_cat/plugins?v', 200, ''],
            ['https://localhost:9200/_cat/health?v', 200, 'green'],
        ]
        # Use http in the request url if the security plugin is absent
        if not security_plugin_exists:
            for api in test_apis:
                api[0] = "http" + api[0][5:]  # type: ignore

        if ("opensearch-dashboards" in projects):
            test_apis.append(['http://localhost:5601/api/status', 200, ''])

        for test_api in test_apis:
            request_url = test_api.__getitem__(0)
            success_status_code = test_api.__getitem__(1)
            validate_string = test_api.__getitem__(2)

            status_code, response_text = ApiTest(str(request_url), version).api_get()
            logging.info(f"\nRequest_url ->{str(request_url)} \n")
            logging.info(f"\nStatus_code ->{status_code} \nresponse_text ->{response_text}")

            if status_code == success_status_code and (not validate_string or validate_string in response_text):
                pass_counter += 1
            else:
                fail_counter += 1

        return (fail_counter == 0, f"There are {pass_counter}/{pass_counter + fail_counter} test cases Pass")
