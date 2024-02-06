import logging
import os

from system.process import Process
from system.temporary_directory import TemporaryDirectory
from system.zip_file import ZipFile
from validation_workflow.download_utils import DownloadUtils
from validation_workflow.validation import Validation
from validation_workflow.validation_args import ValidationArgs


class ValidateWin(Validation, DownloadUtils):

    def __init__(self, args: ValidationArgs) -> None:
        super().__init__(args)
        self.base_url_production = "https://artifacts.opensearch.org/releases/bundle/"
        self.base_url_staging = "https://ci.opensearch.org/ci/dbc/distribution-build-"
        self.tmp_dir = TemporaryDirectory()
        self.os_process = Process()
        self.osd_process = Process()

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
                        project] = f"{self.base_url_staging}{project}/{self.args.version}/{self.args.build_number[project]}/windows/{self.args.arch}/{self.args.distribution}/dist/{project}/{project}-{self.args.version}-windows-{self.args.arch}.zip"  # noqa: E501
                else:
                    self.args.file_path[
                        project] = f"{self.base_url_production}{project}/{self.args.version}/{project}-{self.args.version}-windows-{self.args.arch}.zip"
                self.check_url(self.args.file_path.get(project))
        return True

    def installation(self) -> bool:
        try:
            for project in self.args.projects:
                logging.info(project)
                filename = os.path.basename(self.args.file_path.get(project))
                work_dir = os.path.join(self.tmp_dir.path, project)
                self.os_process('mkdir ' + work_dir, ".", True)
                logging.info(f" Installing in {work_dir}/{filename.split('.')[0]}/opensearch-{self.args.version}")
                with ZipFile(os.path.join(self.tmp_dir.path, filename), "r") as zip:
                    zip.extractall(work_dir)

            if self.args.allow_without_security:
                self.args.allow_without_security = self.test_security_plugin(str(self.tmp_dir.path))
        except:
            raise Exception('Failed to install Opensearch')
        return True
