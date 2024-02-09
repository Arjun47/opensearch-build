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
from system.execute import execute

from validation_workflow.download_utils import DownloadUtils
from validation_workflow.api_test_cases import ApiTestCases
from validation_workflow.validation import Validation
from validation_workflow.validation_args import ValidationArgs


class ValidateWin(Validation, DownloadUtils):
    def __init__(self, args: ValidationArgs) -> None:
        super().__init__(args)
        self.os_process = Process()
        self.osd_process = Process()

    def installation(self) -> bool:
        try:
            for project in self.args.projects:
                logging.info(project)
                self.set_password_env("deb")
                self.os_process.start(f"sudo dpkg -i {os.path.basename(self.args.file_path.get(project))}", ".", True)
                time.sleep(80)

        except:
            raise Exception("Failed to install Opensearch")
        return True

    def start_cluster(self) -> bool:
        try:
            for project in self.args.projects:
                execute(f'sudo systemctl enable {project} && sudo systemctl start {project}', ".")
                time.sleep(20)
                (stdout, stderr, status) = execute(f'sudo systemctl status {project}', ".")
                if(status == 0):
                    logging.info(stdout)
                else:
                    logging.info(stderr)

        except:
            raise Exception('Failed to Start Cluster')
        return True

    def validation(self) -> bool:
        logging.info(self.args.force_https_check)
        test_result, counter = ApiTestCases().test_apis(self.args.version, self.args.projects, self.check_for_security_plugin(os.path.join(os.sep, "usr", "share", "opensearch"), "deb") if not self.args.force_https_check else True)  # noqa: E501
        if (test_result):
            logging.info(f'All tests Pass : {counter}')
            return True
        else:
            raise Exception(f'Not all tests Pass : {counter}')

    def cleanup(self) -> bool:
        try:
            for project in self.args.projects:
                execute(f'sudo systemctl stop {project}', ".")
                execute(f'sudo yum remove {project} -y', ".")
        except Exception as e:
            raise Exception(
                f'Exception occurred either while attempting to stop cluster or removing OpenSearch/OpenSearch-Dashboards. {str(e)}')
        return True
