# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import unittest
from unittest.mock import MagicMock, Mock, patch

from system.process import Process
from validation_workflow.tar.validation_tar import ValidateTar
from validation_workflow.validation import Validation

class TestValidateTar(unittest.TestCase):
    def setUp(self):
        # Set up a mock instance for testing
        self.args = Mock()
        self.call_methods = ValidateTar(self.args)

    @patch("validation_workflow.download_utils.DownloadUtils", return_value=True)
    @patch('validation_workflow.tar.validation_tar.ValidationArgs')
    def test_download_artifacts(self, mock_validation_args: Mock, mock_download_utils: Mock) -> None:
        mock_isFilePathEmpty = Mock()
        mock_isFilePathEmpty.return_value = False
        mock_validation_args.return_value.artifact_type.return_value = "staging"
        mock_validation_args.return_value.projects.return_value = ["opensearch"]
        mock_validation_args.return_value.version.return_value = "2.5.0"
        mock_validation_args.return_value.arch.return_value = "x64"

        validate_tar = ValidateTar(mock_validation_args.return_value)

        with patch.object(validate_tar, 'check_url') as mock_check_url:
            mock_check_url.return_value = True
            result = validate_tar.download_artifacts()
            self.assertTrue(result)

    def test_empty_file_path_and_production_artifact_type(self):
        self.args.projects = ["opensearch"]
        self.args.version = "2.4.0"
        self.args.file_path = {}
        self.args.artifact_type = "production"

        with patch.object(self.call_methods, 'check_url') as mock_check_url:
            result = self.call_methods.download_artifacts()

        self.assertTrue(result)
        mock_check_url.assert_called_once()

    def test_empty_file_path_and_staging_artifact_type(self):
        self.args.projects = ["opensearch"]
        self.args.version = "2.4.0"
        self.args.artifact_type = "production"
        self.args.file_path = {"opensearch": "https://ci.opensearch.org/ci/dbc/distribution-build-opensearch/1.3.12/latest/linux/x64/rpm/dist/opensearch/opensearch-1.3.12.staging.repo"}

        with patch.object(self.call_methods, 'check_url') as mock_check_url:
            result = self.call_methods.download_artifacts()

        self.assertTrue(result)

        mock_check_url.assert_called_with(self.args.file_path["opensearch"])

    @patch('shutil.copy2', return_value=True)
    def test_local_artifacts(self, mock_mkdir):
        self.args.file_path = {"opensearch": "tar.gz"}
        self.args.projects = ["opensearch"]
        self.args.version = ""
        self.args.arch = "x64"

        with patch.object(self.call_methods, 'copy_artifact') as mock_copy_artifact:
            result = self.call_methods.download_artifacts()
        self.assertTrue(result)
        mock_copy_artifact.assert_called_once()






    @patch("validation_workflow.download_utils.DownloadUtils.is_url_valid", return_value=True)
    @patch("validation_workflow.download_utils.DownloadUtils.download", return_value=True)
    @patch("validation_workflow.validation.Validation.check_url", return_value=True)
    @patch('validation_workflow.tar.validation_tar.ValidationArgs')
    def test_download_artifacts_error(self, mock_validation_args: Mock, mock_is_url_valid: Mock, mock_download: Mock, mock_check_url: Mock) -> None:
        url = "https://opensearch.org/release/2.11.0/opensearch-2.11.0-linux-arm64.tar.gz"

        validate_tar = ValidateTar(mock_validation_args)
        validate_tar.download_artifacts()
        self.assertRaises(Exception, validate_tar.check_url(url))

    @patch('validation_workflow.tar.validation_tar.ValidationArgs')
    def test_copy_artifacts(self, mock_validation_args: Mock) -> None:
        mock_validation_args.return_value.projects = ["opensearch", "opensearch-dashboards"]
        mock_validation_args.return_value.file_path = {"opensearch": "/src/files/opensearch-tar.gz", "opensearch-dashboards": "/src/files/opensearch-dashboards-tar.gz"}
        validate_tar = ValidateTar(mock_validation_args.return_value)

        # Call cleanup method
        with patch.object(validate_tar, 'copy_artifact') as mock_copy_artifact:
            mock_copy_artifact.return_value = True
            result = validate_tar.download_artifacts()
            self.assertTrue(result)
    @patch("validation_workflow.tar.validation_tar.execute", return_value=True)
    @patch('validation_workflow.tar.validation_tar.ValidationArgs')
    def test_installation(self, mock_validation_args: Mock, mock_system: Mock) -> None:
        mock_validation_args.return_value.version.return_value = '2.3.0'
        mock_validation_args.return_value.arch.return_value = 'x64'
        mock_validation_args.return_value.platform.return_value = 'linux'
        mock_validation_args.return_value.projects.return_value = ["opensearch"]

        validate_tar = ValidateTar(mock_validation_args.return_value)

        result = validate_tar.installation()
        self.assertTrue(result)

    @patch('validation_workflow.tar.validation_tar.ValidationArgs')
    @patch.object(Process, 'start')
    @patch('time.sleep')
    def test_start_cluster(self, mock_sleep: Mock, mock_start: Mock, mock_validation_args: Mock) -> None:
        validate_tar = ValidateTar(mock_validation_args.return_value)
        result = validate_tar.start_cluster()
        self.assertTrue(result)

    @patch('validation_workflow.tar.validation_tar.ValidationArgs')
    @patch('validation_workflow.tar.validation_tar.ApiTestCases')
    def test_validation(self, mock_test_apis: Mock, mock_validation_args: Mock) -> None:
        mock_validation_args.return_value.version = '2.3.0'
        mock_test_apis_instance = mock_test_apis.return_value
        mock_test_apis_instance.test_apis.return_value = (True, 3)

        validate_tar = ValidateTar(mock_validation_args.return_value)

        result = validate_tar.validation()
        self.assertTrue(result)

        mock_test_apis.assert_called_once()

    @patch('validation_workflow.tar.validation_tar.ValidationArgs')
    @patch('validation_workflow.tar.validation_tar.ApiTestCases')
    def test_failed_testcases(self, mock_test_apis: Mock, mock_validation_args: Mock) -> None:
        # Set up mock objects
        mock_validation_args.return_value.version = '2.3.0'
        mock_test_apis_instance = mock_test_apis.return_value
        mock_test_apis_instance.test_apis.return_value = (True, 1)

        # Create instance of ValidateRpm class
        validate_tar = ValidateTar(mock_validation_args.return_value)

        # Call validation method and assert the result
        validate_tar.validation()
        self.assertRaises(Exception, "Not all tests Pass : 1")

        # Assert that the mock methods are called as expected
        mock_test_apis.assert_called_once()

    @patch('validation_workflow.tar.validation_tar.ValidationArgs')
    @patch.object(Process, 'terminate')
    def test_cleanup(self, mock_terminate: Mock, mock_validation_args: Mock) -> None:
        validation_args = mock_validation_args.return_value
        validate_tar = ValidateTar(validation_args)
        result = validate_tar.cleanup()
        self.assertTrue(result)
