# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import logging
import os
import time

from system.process import Process
from system.zip_file import ZipFile
from test_workflow.integ_test.utils import get_password
from validation_workflow.api_test_cases import ApiTestCases
from validation_workflow.download_utils import DownloadUtils
from validation_workflow.validation import Validation
from validation_workflow.validation_args import ValidationArgs


class ValidateZip(Validation, DownloadUtils):
    def __init__(self, args: ValidationArgs) -> None:
        super().__init__(args)
        self.os_process = Process()
        self.osd_process = Process()

    def installation(self) -> bool:
        try:
            for project in self.args.projects:
                with ZipFile(os.path.join(self.tmp_dir.path, os.path.basename(self.args.file_path.get(project))), "r") as zip:
                    zip.extractall(self.tmp_dir.path)
        except Exception as e:
            raise Exception("Failed to install Opensearch")
        return True

    def start_cluster(self) -> bool:
        try:
            self.os_process.start(f"env OPENSEARCH_INITIAL_ADMIN_PASSWORD={get_password(str(self.args.version))} .\\opensearch-windows-install.bat", os.path.join(self.tmp_dir.path, f"opensearch-{self.args.version}"), False)  # noqa: E501
            time.sleep(85)
            if "opensearch-dashboards" in self.args.projects:
                self.osd_process.start(".\\bin\\opensearch-dashboards.bat", os.path.join(self.tmp_dir.path, f"opensearch-dashboards-{self.args.version}"), False)
                time.sleep(20)
            logging.info("Starting cluster")
        except:
            raise Exception('Failed to Start Cluster')
        return True

    def validation(self) -> bool:
        test_result, counter = ApiTestCases().test_apis(self.args.version, self.args.projects, self.check_for_security_plugin(os.path.join(self.tmp_dir.path, "opensearch")) if not self.args.force_https else True)  # noqa: E501
        if test_result:
            logging.info(f'All tests Pass : {counter}')
        else:
            raise Exception(f'Not all tests Pass : {counter}')
        return True

    def cleanup(self) -> bool:
        try:
            self.os_process.terminate()
            if ("opensearch-dashboards" in self.args.projects):
                self.osd_process.terminate()
        except:
            raise Exception('Failed to terminate the processes that started OpenSearch and OpenSearch-Dashboards')
        return True
