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
        self.base_url_production = "https://artifacts.opensearch.org/releases/bundle/"
        self.base_url_staging = "https://ci.opensearch.org/ci/dbc/distribution-build-"
        self.tmp_dir = TemporaryDirectory()
        self.file_name = ""
        self.os_process = Process()
        self.osd_process = Process()

        # if (self.args.file_path == "local"):
        # get the file name from os.path.basename(url)
        # self.filename = os.path.basename(self.filename)
        # self.copy_artifact(self.args.path, str(self.tmp_dir.path))
        # file_name1 = os.path.basename('/root/file.ext')
        # print(self.filename, type(self.filename[0]), "1")

    def download_artifacts(self) -> bool:
        for project in self.args.projects:
            if (self.args.file_path):
                self.check_url(self.args.file_path)
            else:
                self.args.file_path = f"{self.base_url_production}{project}/{self.args.version}/{project}-{self.args.version}-linux-{self.args.arch}.tar.gz"
                self.check_url(self.args.file_path)
        return True

    def installation(self) -> bool:
        try:
            self.filename = os.path.basename(self.args.file_path)
            print(self.filename)

            execute('mkdir ' + str(self.tmp_dir.path) + '/opensearch | tar -xzf ' + os.path.join(str(self.tmp_dir.path), self.filename) + ' -C ' + str(self.tmp_dir.path) + '/opensearch --strip-components=1', ".", True, False)  # noqa: E501
        except:
            raise Exception('Failed to Install Opensearch')
        return True

    def start_cluster(self) -> bool:
        try:
            self.os_process.start(os.path.join(self.tmp_dir.path, "opensearch", "opensearch-tar-install.sh"), ".")
            time.sleep(85)
            logging.info('Started cluster')
            time.sleep(20)
        except:
            raise Exception('Failed to Start Cluster')
        return True

    def validation(self) -> bool:
        test_result, counter = ApiTestCases().test_cases(self.args.projects)
        if (test_result):
            logging.info(f'All tests Pass : {counter}')
        else:
            raise Exception(f'Not all tests Pass : {counter}')
        return True

    def cleanup(self) -> bool:
        try:
            self.os_process.terminate()
        except:
            raise Exception('Failed to terminate the processes that started OS and OSD')
        return True
