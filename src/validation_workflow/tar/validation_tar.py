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
from system.temporary_directory import TemporaryDirectory
from validation_workflow.api_test_cases import ApiTestCases
from validation_workflow.download_utils import DownloadUtils
from validation_workflow.validation import Validation
from validation_workflow.validation_args import ValidationArgs


class ValidateTar(Validation, DownloadUtils):

    def __init__(self, args: ValidationArgs) -> None:
        super().__init__(args)
        self.base_url = "https://artifacts.opensearch.org/releases/bundle/"
        self.tmp_dir = TemporaryDirectory()
        self.file_name = ""
        self.os_process = Process()
        self.osd_process = Process()

    def download_artifacts(self) -> bool:
        for project in self.args.projects:
            if (self.args.download_source == "local"):
                self.filename = os.path.basename(self.filename)
                self.copy_artifact(self.args.path, str(self.tmp_dir.path))
                file_name1 = os.path.basename('/root/file.ext')
                print(self.filename, type(self.filename[0]), "1")
            else:
                url = f"{self.base_url}{project}/{self.args.version}/{project}-{self.args.version}-linux-{self.args.arch}.tar.gz"
                self.check_url(url)
        return True

    def installation(self) -> bool:
        try:
            for project in self.args.projects:

                fileName = f"{project}-{self.args.version}-{self.args.platform}-{self.args.arch}"
                execute('tar -zxf ' + os.path.join(str(self.tmp_dir.path), fileName) + '.tar.gz -C ' + str(self.tmp_dir.path), ".", True, False)
        except:
            raise Exception('Failed to Install Opensearch')
        return True

    def start_cluster(self) -> bool:
        try:
            self.os_process.start(os.path.join(self.tmp_dir.path, "opensearch-" + self.args.version, "opensearch-tar-install.sh"), ".")
            time.sleep(85)
            logging.info('Started cluster')
            self.osd_process.start(os.path.join(str(self.tmp_dir.path), "opensearch-dashboards-" + self.args.version, "bin", "opensearch-dashboards"), ".")
            time.sleep(20)
        except:
            raise Exception('Failed to Start Cluster')
        return True

    def validation(self) -> bool:
        test_result, counter = ApiTestCases().test_cases()
        if (test_result):
            logging.info(f'All tests Pass : {counter}')
        else:
            raise Exception(f'Not all tests Pass : {counter}')
        return True

    def cleanup(self) -> bool:
        try:
            self.os_process.terminate()
            self.osd_process.terminate()
        except:
            raise Exception('Failed to terminate the processes that started OS and OSD')
        return True
