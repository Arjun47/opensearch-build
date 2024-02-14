# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import unittest
from unittest.mock import MagicMock, Mock, patch, call

from system.process import Process
from validation_workflow.zip.validation_zip import ValidateZip


class TestValidateZip(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_args = MagicMock()
        self.mock_args.projects = ["opensearch", "opensearch-dashboards"]
        self.mock_args.file_path = {"opensearch": "/src/opensearch/opensearch-1.3.12.zip", "opensearch-dashboards": "/src/opensearch-dashboards/opensearch-dashboards-1.3.12.zip"}
        self.mock_args.version = "2.3.0"
        self.mock_args.arch = "x64"
        self.mock_args.platform = "windows"
        self.mock_args.force_https_check = True
        self.mock_args.allow_without_security = True
        self.call_methods = ValidateZip(self.mock_args)

    @patch("validation_workflow.zip.validation_zip.ZipFile")
    def test_installation(self, mock_zip_file: MagicMock) -> None:
        mock_zip_file_instance = mock_zip_file.return_value.__enter__()
        mock_extractall = MagicMock()
        mock_zip_file_instance.extractall = mock_extractall

        validate_zip = ValidateZip(self.mock_args)
        result = validate_zip.installation()
        self.assertTrue(result)

        # Assert that extractall was called once for each project
        expected_calls = [call((validate_zip.tmp_dir.path))] * len(self.mock_args.projects)
        mock_extractall.assert_has_calls(expected_calls)

    @patch("validation_workflow.zip.validation_zip.ZipFile")
    def test_installation_exception(self, mock_zip_file: MagicMock) -> None:
        # to make for loop error out
        self.mock_args.projects = None
        validate_zip = ValidateZip(self.mock_args)
        with self.assertRaises(Exception) as context:
            validate_zip.installation()
        self.assertEqual(str(context.exception), "Failed to install Opensearch")

    @patch.object(Process, 'start')
    @patch("time.sleep")
    def test_start_cluster(self, mock_sleep: Mock, mock_start: Mock) -> None:

        validate_zip = ValidateZip(self.mock_args)
        result = validate_zip.start_cluster()
        self.assertTrue(result)
        expected_calls = [
            call('env OPENSEARCH_INITIAL_ADMIN_PASSWORD=admin .\\opensearch-windows-install.bat',
                      f'{validate_zip.tmp_dir.path}\\opensearch-2.3.0', False),
            call (
            '.\\bin\\opensearch-dashboards.bat', f'{validate_zip.tmp_dir.path}\\opensearch-dashboards-2.3.0', False)
        ]
        mock_start.assert_has_calls(expected_calls)
