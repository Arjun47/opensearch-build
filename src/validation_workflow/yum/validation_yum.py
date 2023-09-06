# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import logging
import time

from system.execute import execute
from system.temporary_directory import TemporaryDirectory
from validation_workflow.api_test_cases import ApiTestCases
from validation_workflow.download_utils import DownloadUtils
from validation_workflow.validation import Validation
from validation_workflow.validation_args import ValidationArgs


class ValidateYum(Validation, DownloadUtils):

    def __init__(self, args: ValidationArgs) -> None:
        super().__init__(args)
        self.base_url = "https://artifacts.opensearch.org/releases/bundle/"
        self.tmp_dir = TemporaryDirectory()

        # shutil.copy2(localfilepath, temporaryfile_path)

    def download_artifacts(self) -> bool:
        for project in self.args.projects:
            url = f"{self.base_url}{project}/{self.args.version[0:1]}.x/{project}-{self.args.version[0:1]}.x.repo"
            self.check_url(url)
        return True

    def installation(self) -> bool:
        try:
            execute('sudo rpm --import https://artifacts.opensearch.org/publickeys/opensearch.pgp', str(self.tmp_dir.path), True, False)
            for project in self.args.projects:
                execute(f'sudo yum remove {project} -y', ".")
                logging.info('Removed previous versions of Opensearch')
                urllink = f"{self.base_url}{project}/{self.args.version[0:1]}.x/{project}-{self.args.version[0:1]}.x.repo -o /etc/yum.repos.d/{project}-{self.args.version[0:1]}.x.repo"
                execute(f'sudo curl -SL {urllink}', ".")
                execute(f"sudo yum install '{project}-{self.args.version}' -y", ".")
        except:
            raise Exception('Failed to install Opensearch')
        return True

    def start_cluster(self) -> bool:
        try:
            for project in self.args.projects:
                execute(f'sudo systemctl start {project}', ".")
                time.sleep(20)
                execute(f'sudo systemctl status {project}', ".")
        except:
            raise Exception('Failed to Start Cluster')
        return True

    def validation(self) -> bool:
        test_result, counter = ApiTestCases().test_cases(self.args.projects)
        if (test_result):
            logging.info(f'All tests Pass : {counter}')
            return True
        else:
            raise Exception(f'Some test cases failed : {counter}')

    def cleanup(self) -> bool:
        try:
            for project in self.args.projects:
                execute(f'sudo systemctl stop {project}', ".")
                execute(f'sudo yum remove {project} -y', ".")
        except Exception as e:
            raise Exception(f'Exception occurred either while attempting to stop cluster or removing OpenSearch/OpenSearch-Dashboards. {str(e)}')
        return True
