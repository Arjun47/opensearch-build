# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import unittest
from unittest.mock import Mock, patch

from system.temporary_directory import TemporaryDirectory
from validation_workflow.tar.validation_tar import ValidateTar
from validation_workflow.validation import Validation
from validation_workflow.validation_args import ValidationArgs


class ImplementValidation(Validation):
    def __init__(self, args: ValidationArgs) -> None:
        super().__init__(args)

    def installation(self) -> None:
        return None

    def start_cluster(self) -> None:
        return None

    def validation(self) -> None:
        return None

    def cleanup(self) -> None:
        return None


class TestValidation(unittest.TestCase):

    @patch('validation_workflow.download_utils.DownloadUtils')
    @patch('validation_workflow.tar.validation_tar.ValidationArgs')
    def test_check_url_valid(self, mock_validation_args: Mock, mock_download_utils: Mock) -> None:
        mock_validation_args.projects.return_value = ["opensearch"]

        mock_validation = ValidateTar(mock_validation_args.return_value)
        mock_download_utils_download = mock_download_utils.return_value
        mock_download_utils_download.download.return_value = True
        mock_download_utils_download.is_url_valid.return_value = True
        url = "https://ci.opensearch.org/ci/dbc/distribution-build-opensearch/1.3.12/latest/linux/x64/rpm/dist/opensearch/opensearch-1.3.12.staging.repo"

        result = mock_validation.check_url(url)
        self.assertTrue(result)

    @patch('shutil.copy2', return_value=True)
    @patch('validation_workflow.tar.validation_tar.ValidationArgs')
    def test_copy_artifact(self, mock_validation_args: Mock, mock_copy: Mock) -> None:
        mock_validation_args.projects.return_value = ["opensearch"]
        mock_validation = ValidateTar(mock_validation_args.return_value)

        url = "https://ci.opensearch.org/ci/dbc/distribution-build-opensearch/1.3.12/latest/linux/x64/rpm/dist/opensearch/opensearch-1.3.12.staging.repo"

        result = mock_validation.copy_artifact(url, "tmp/tthcdhfh/")
        self.assertTrue(result)

    @patch('os.path.exists')
    @patch('validation_workflow.tar.validation_tar.ValidationArgs')
    def test_check_for_security_plugin(self, mock_validation_args: Mock, mock_path_exists: Mock) -> None:
        mock_path_exists.return_value = True

        mock_validation_args.projects.return_value = ["opensearch"]
        mock_validation = ValidateTar(mock_validation_args.return_value)

        result = mock_validation.check_for_security_plugin("/tmp/tmkuiuo/opensearch")

        self.assertTrue(result)

    @patch('validation_workflow.validation.execute')
    @patch('validation_workflow.tar.validation_tar.ValidationArgs')
    def test_check_for_security_plugin_false(self, mock_validation_args: Mock, mock_execute: Mock) -> None:
        mock_execute.return_value = (0, "opensearch", "")

        mock_validation_args.projects.return_value = ["opensearch"]
        mock_validation = ValidateTar(mock_validation_args.return_value)

        result = mock_validation.check_for_security_plugin("/bin/opensearch", "tar")

        self.assertFalse(result)

    @patch('validation_workflow.validation.Validation.check_url')
    @patch('validation_workflow.validation.Validation.copy_artifact')
    @patch('validation_workflow.download_utils.DownloadUtils')
    @patch('validation_workflow.validation.ValidationArgs')
    def test_download_artifacts_with_url(self, mock_validation_args: Mock, mock_download_utils: Mock, mock_copy_artifact: Mock, mock_check_url: Mock) -> None:
        mock_copy_artifact.return_value = True
        mock_validation_args.return_value.projects = ["opensearch"]
        mock_validation_args.return_value.file_path = {"opensearch": "https://ci.opensearch.org/ci/dbc/distribution-build-opensearch/1.3.12/latest/linux/x64/rpm/dist/opensearch/opensearch-1.3.12.staging.repo"}
        mock_download_utils.return_value.download.return_value = True
        mock_download_utils.return_value.is_url_valid.return_value = True
        mock_validation = ImplementValidation(mock_validation_args.return_value)

        # Call the download_artifacts method
        result = mock_validation.download_artifacts()

        # Assertions
        self.assertTrue(result)
        self.assertEqual(mock_validation.args.version, "1.3.12")

    @patch('validation_workflow.validation.Validation.check_url')
    @patch('validation_workflow.validation.Validation.copy_artifact')
    @patch('validation_workflow.download_utils.DownloadUtils')
    @patch('validation_workflow.validation.ValidationArgs')
    def test_download_artifacts_local_path(self, mock_validation_args: Mock, mock_download_utils: Mock, mock_copy_artifact: Mock, mock_check_url: Mock) -> None:
        mock_copy_artifact.return_value = True
        mock_validation_args.return_value.projects = ["opensearch"]
        mock_validation_args.return_value.file_path = {"opensearch": "/rpm/dist/opensearch/opensearch-1.3.12.staging.repo"}
        mock_download_utils.return_value.download.return_value = True
        mock_download_utils.return_value.is_url_valid.return_value = True
        mock_validation = ImplementValidation(mock_validation_args.return_value)

        # Call the download_artifacts method
        result = mock_validation.download_artifacts()

        # Assertions
        self.assertTrue(result)
        self.assertNotEqual(mock_validation.args.version, "1.3.12")

    @patch('validation_workflow.validation.Validation.check_url')
    @patch('validation_workflow.validation.Validation.copy_artifact')
    @patch('validation_workflow.download_utils.DownloadUtils')
    @patch('validation_workflow.validation.ValidationArgs')
    def test_download_artifacts_empty_file_path_staging_tar(self, mock_validation_args: Mock, mock_download_utils: Mock, mock_copy_artifact: Mock, mock_check_url: Mock) -> None:
        # mock_copy_artifact.return_value = True
        mock_validation_args.return_value.projects = ["opensearch"]
        mock_validation_args.return_value.version = "1.3.12"
        mock_validation_args.return_value.build_number = {"opensearch": "98765"}
        mock_validation_args.return_value.file_path = {}
        mock_validation_args.return_value.platform = "linux"
        mock_validation_args.return_value.arch = "x64"
        mock_validation_args.return_value.distribution = "tar"
        mock_validation_args.return_value.artifact_type = "staging"
        mock_download_utils.return_value.download.return_value = True
        mock_download_utils.return_value.is_url_valid.return_value = True
        mock_validation = ImplementValidation(mock_validation_args.return_value)

        # Call the download_artifacts method
        result = mock_validation.download_artifacts()
        expected_uri = 'https://ci.opensearch.org/ci/dbc/distribution-build-opensearch/1.3.12/98765/linux/x64/tar/dist/opensearch/opensearch-1.3.12-linux-x64.tar.gz'

        # Assertions
        self.assertTrue(result)
        self.assertEqual(mock_validation.args.file_path["opensearch"], expected_uri)
        mock_check_url.assert_called_with(expected_uri)
    @patch('validation_workflow.validation.Validation.check_url')
    @patch('validation_workflow.validation.Validation.copy_artifact')
    @patch('validation_workflow.download_utils.DownloadUtils')
    @patch('validation_workflow.validation.ValidationArgs')
    def test_download_artifacts_empty_file_path_production_deb(self, mock_validation_args: Mock, mock_download_utils: Mock, mock_copy_artifact: Mock, mock_check_url: Mock) -> None:
        # mock_copy_artifact.return_value = True
        mock_validation_args.return_value.projects = ["opensearch"]
        mock_validation_args.return_value.version = "1.3.12"
        mock_validation_args.return_value.build_number = {"opensearch": "98765"}
        mock_validation_args.return_value.file_path = {}
        mock_validation_args.return_value.platform = "linux"
        mock_validation_args.return_value.arch = "x64"
        mock_validation_args.return_value.distribution = "deb"
        mock_validation_args.return_value.artifact_type = "production"
        mock_download_utils.return_value.download.return_value = True
        mock_download_utils.return_value.is_url_valid.return_value = True
        mock_validation = ImplementValidation(mock_validation_args.return_value)

        # Call the download_artifacts method
        result = mock_validation.download_artifacts()
        expected_uri = 'https://artifacts.opensearch.org/releases/bundle/opensearch/1.3.12/opensearch-1.3.12-linux-x64.deb'

        # Assertions
        self.assertTrue(result)
        self.assertEqual(mock_validation.args.file_path["opensearch"], expected_uri)
        mock_check_url.assert_called_with(expected_uri)

    @patch('validation_workflow.validation.Validation.check_url')
    @patch('validation_workflow.validation.Validation.copy_artifact')
    @patch('validation_workflow.download_utils.DownloadUtils')
    @patch('validation_workflow.validation.ValidationArgs')
    def test_download_artifacts_empty_file_path_staging_yum(self, mock_validation_args: Mock, mock_download_utils: Mock, mock_copy_artifact: Mock, mock_check_url: Mock) -> None:
        # mock_copy_artifact.return_value = True
        mock_validation_args.return_value.projects = ["opensearch"]
        mock_validation_args.return_value.version = "1.3.12"
        mock_validation_args.return_value.build_number = {"opensearch": "98765"}
        mock_validation_args.return_value.file_path = {}
        mock_validation_args.return_value.platform = "linux"
        mock_validation_args.return_value.arch = "x64"
        mock_validation_args.return_value.distribution = "yum"
        mock_validation_args.return_value.artifact_type = "staging"
        mock_download_utils.return_value.download.return_value = True
        mock_download_utils.return_value.is_url_valid.return_value = True
        mock_validation = ImplementValidation(mock_validation_args.return_value)

        # Call the download_artifacts method
        result = mock_validation.download_artifacts()
        expected_uri = 'https://ci.opensearch.org/ci/dbc/distribution-build-opensearch/1.3.12/98765/linux/x64/rpm/dist/opensearch/opensearch-1.3.12.staging.repo'

        # Assertions
        self.assertTrue(result)
        self.assertEqual(mock_validation.args.file_path["opensearch"], expected_uri)
        mock_check_url.assert_called_with(expected_uri)

    @patch('validation_workflow.validation.Validation.check_url')
    @patch('validation_workflow.validation.Validation.copy_artifact')
    @patch('validation_workflow.download_utils.DownloadUtils')
    @patch('validation_workflow.validation.ValidationArgs')
    def test_download_artifacts_empty_file_path_production_yum(self, mock_validation_args: Mock, mock_download_utils: Mock, mock_copy_artifact: Mock, mock_check_url: Mock) -> None:
        # mock_copy_artifact.return_value = True
        mock_validation_args.return_value.projects = ["opensearch"]
        mock_validation_args.return_value.version = "1.3.12"
        mock_validation_args.return_value.build_number = {"opensearch": "98765"}
        mock_validation_args.return_value.file_path = {}
        mock_validation_args.return_value.platform = "linux"
        mock_validation_args.return_value.arch = "x64"
        mock_validation_args.return_value.distribution = "yum"
        mock_validation_args.return_value.artifact_type = "production"
        mock_download_utils.return_value.download.return_value = True
        mock_download_utils.return_value.is_url_valid.return_value = True
        mock_validation = ImplementValidation(mock_validation_args.return_value)

        # Call the download_artifacts method
        result = mock_validation.download_artifacts()
        expected_uri = 'https://artifacts.opensearch.org/releases/bundle/opensearch/1.x/opensearch-1.x.repo'

        # Assertions
        self.assertTrue(result)
        self.assertEqual(mock_validation.args.file_path["opensearch"], expected_uri)
        mock_check_url.assert_called_with(expected_uri)