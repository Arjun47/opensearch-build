# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import logging
import os
import time

from system.execute import execute
from system.process import Process
from test_workflow.integ_test.utils import get_password
from validation_workflow.api_test_cases import ApiTestCases
from validation_workflow.download_utils import DownloadUtils
from validation_workflow.validation import Validation
from validation_workflow.validation_args import ValidationArgs


class ValidateTar(Validation, DownloadUtils):

    def __init__(self, args: ValidationArgs) -> None:
        super().__init__(args)
        self.os_process = Process()
        self.osd_process = Process()

    def installation(self) -> bool:
        try:
            for project in self.args.projects:
                self.filename = os.path.basename(self.args.file_path.get(project))
                execute('mkdir ' + os.path.join(self.tmp_dir.path, project) + ' | tar -xzf ' + os.path.join(str(self.tmp_dir.path), self.filename) + ' -C ' + os.path.join(self.tmp_dir.path, project) + ' --strip-components=1', ".", True, False)  # noqa: E501
        except:
            raise Exception('Failed to install Opensearch')
        return True

    def start_cluster(self) -> bool:
        try:
            self.os_process.start(f'export OPENSEARCH_INITIAL_ADMIN_PASSWORD={get_password(str(self.args.version))} && ./opensearch-tar-install.sh', os.path.join(self.tmp_dir.path, "opensearch"))
            time.sleep(85)
            if ("opensearch-dashboards" in self.args.projects):
                self.osd_process.start(os.path.join(str(self.tmp_dir.path), "opensearch-dashboards", "bin", "opensearch-dashboards"), ".")
                time.sleep(20)
            logging.info('Started cluster')
        except:
            raise Exception('Failed to Start Cluster')
        return True

    def validation(self) -> bool:
        logging.info(self.args.force_https_check)
        test_result, counter = ApiTestCases().test_apis(self.args.version, self.args.projects, self.check_for_security_plugin(os.path.join(self.tmp_dir.path, "opensearch"), "tar") if not self.args.force_https_check else True)  # noqa: E501
        if (test_result):
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
