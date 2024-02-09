# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.


import logging
import os
import re
import shutil
from abc import ABC, abstractmethod
from typing import Any

from system.execute import execute
from test_workflow.integ_test.utils import get_password
from validation_workflow.download_utils import DownloadUtils
from validation_workflow.validation_args import ValidationArgs
from system.temporary_directory import TemporaryDirectory


class Validation(ABC):
    """
        Abstract class for all types of artifact validation
    """

    def __init__(self, args: ValidationArgs) -> None:
        self.args = args
        self.base_url_production = "https://artifacts.opensearch.org/releases/bundle/"
        self.base_url_staging = "https://ci.opensearch.org/ci/dbc/distribution-build-"
        self.tmp_dir = TemporaryDirectory()

    def check_url(self, url: str) -> bool:
        if DownloadUtils().download(url, self.tmp_dir) and DownloadUtils().is_url_valid(url):  # type: ignore
            logging.info(f"Valid URL - {url} and Download Successful !")
            return True
        else:
            raise Exception(f"Invalid url - {url}")

    def copy_artifact(self, filepath: str, tempdir_path: str) -> bool:
        if filepath:
            shutil.copy2(filepath, tempdir_path)
            return True
        else:
            raise Exception("Provided path for local artifacts does not exist")

    def check_for_security_plugin(self, work_dir: str, distribution: str) -> bool:
        path = os.path.exists(os.path.join(work_dir, "plugins", "opensearch-security"))
        logging.info(path)
        return path

    def get_version(self, project: str) -> str:
        return re.search(r'(\d+\.\d+\.\d+)', os.path.basename(project)).group(1)

    def run(self) -> Any:
        try:
            return self.download_artifacts() and self.installation() and self.start_cluster() and self.validation() and self.cleanup()
        except Exception as e:
            raise Exception(f'An error occurred while running the validation tests: {str(e)}')

    def download_artifacts(self) -> bool:
        isFilePathEmpty = bool(self.args.file_path)
        for project in self.args.projects:
            if (isFilePathEmpty):
                if ("https:" not in self.args.file_path.get(project)):
                    self.copy_artifact(self.args.file_path.get(project), str(self.tmp_dir.path))
                else:
                    self.args.version = self.get_version(self.args.file_path.get(project))
                    self.check_url(self.args.file_path.get(project))
            else:
                if (self.args.artifact_type == "staging"):
                    self.args.file_path[
                        project] = f"{self.base_url_staging}{project}/{self.args.version}/{self.args.build_number[project]}/linux/{self.args.arch}/{self.args.distribution}/dist/{project}/{project}-{self.args.version}-linux-{self.args.arch}.tar.gz"  # noqa: E501
                else:
                    self.args.file_path[
                        project] = f"{self.base_url_production}{project}/{self.args.version}/{project}-{self.args.version}-linux-{self.args.arch}.tar.gz"
                self.check_url(self.args.file_path.get(project))
        return True

    @abstractmethod
    def installation(self) -> bool:
        pass

    @abstractmethod
    def start_cluster(self) -> bool:
        pass

    @abstractmethod
    def validation(self) -> bool:
        pass

    @abstractmethod
    def cleanup(self) -> bool:
        pass
