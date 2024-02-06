import logging
import os
import time

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
        self.filename = None
        self.zip_path = None

    def download_artifacts(self) -> bool:
        isFilePathEmpty = bool(self.args.file_path)
        for project in self.args.projects:
            if isFilePathEmpty:
                if "https:" not in self.args.file_path.get(project):
                    self.copy_artifact(self.args.file_path.get(project), str(self.tmp_dir.path))
                else:
                    self.args.version = self.get_version(self.args.file_path.get(project))
                    self.check_url(self.args.file_path.get(project))
            else:
                if self.args.artifact_type == "staging":
                    self.args.file_path[
                        project
                    ] = f"{self.base_url_staging}{project}/{self.args.version}/{self.args.build_number[project]}/windows/{self.args.arch}/{self.args.distribution}/dist/{project}/{project}-{self.args.version}-windows-{self.args.arch}.zip"  # noqa: E501
                else:
                    self.args.file_path[
                        project
                    ] = f"{self.base_url_production}{project}/{self.args.version}/{project}-{self.args.version}-windows-{self.args.arch}.zip"
                self.check_url(self.args.file_path.get(project))
        return True

    def installation(self) -> bool:
        try:
            for project in self.args.projects:
                logging.info(project)
                filename = os.path.basename(self.args.file_path.get(project))
                work_dir = os.path.join(self.tmp_dir.path, project)
                self.os_process.start("mkdir " + work_dir, ".", True)
                logging.info(f" Installing in {work_dir}/{filename.split('.')[0]}/opensearch-{self.args.version}")
                self.zip_path = os.path.join(work_dir, f"opensearch-{self.args.version}")
                with ZipFile(os.path.join(self.tmp_dir.path, filename), "r") as zip:
                    zip.extractall(work_dir)

            if self.args.allow_without_security:
                self.args.allow_without_security = self.test_security_plugin(str(self.tmp_dir.path))
        except:
            raise Exception("Failed to install Opensearch")
        return True

    def start_cluster(self) -> bool:
        try:
            self.os_process.start("set OPENSEARCH_INITIAL_ADMIN_PASSWORD=myStrongPassword123!", ".", True)
            self.os_process.start(".\\opensearch-windows-install.bat", self.zip_path, True)
            time.sleep(85)
            if "opensearch-dashboards" in self.args.projects:
                self.os_process.start(
                    ".\\bin\\opensearch-dashboards.bat",
                    os.path.join(
                        self.tmp_dir.path,
                        "opensearch-dashboards",
                        self.filename.split(".")[0],
                        f"opensearch-dashboards-{self.args.version}",
                    ),
                    True,
                )
            logging.info("Starting cluster")
        except:
            raise Exception('Failed to Start Cluster')
        return True

    def validation(self) -> bool:
        logging.info("Inside Validation")
        return True

    def cleanup(self) -> bool:
        logging.info("Inside cleanup")
        return True
