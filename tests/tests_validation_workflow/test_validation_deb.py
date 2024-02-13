# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import unittest
from unittest.mock import MagicMock, Mock, patch

from system.process import Process
from validation_workflow.deb.validation_deb import ValidateDeb


class TestValidateDeb(unittest.TestCase):
    def setUp(self) -> None:
        self.args = Mock()
        self.call_methods = ValidateDeb(self.args)

    @patch('time.sleep')
    @patch('validation_workflow.deb.validation_deb.ValidationArgs')
    @patch('validation_workflow.deb.validation_deb.execute')
    @patch('validation_workflow.deb.validation_deb.Validation.set_password_env')
    def test_installation(self, mock_set_pwd: Mock, mock_system: Mock, mock_validation_args: Mock,
                          mock_sleep: Mock) -> None:
        mock_validation_args.return_value.version = '2.3.0'
        mock_validation_args.return_value.arch = 'x64'
        mock_validation_args.return_value.platform = 'linux'
        mock_validation_args.return_value.force_https_check = True
        mock_validation_args.return_value.projects = ["opensearch"]
        mock_validation_args.return_value.file_path = {"opensearch": "/src/opensearch/opensearch-1.3.12.staging.deb"}

        validate_deb = ValidateDeb(mock_validation_args.return_value)
        # mock_basename.side_effect = lambda path: "mocked_filename"
        mock_system.side_effect = lambda *args, **kwargs: (0, "stdout_output", "stderr_output")
        result = validate_deb.installation()
        self.assertTrue(result)
        mock_set_pwd.assert_called_with("deb")

    @patch('validation_workflow.deb.validation_deb.execute')
    @patch('validation_workflow.deb.validation_deb.ValidationArgs')
    @patch('time.sleep')
    def test_start_cluster(self, mock_sleep: Mock, mock_validation_args: Mock, mock_execute: Mock) -> None:
        mock_validation_args.return_value.version = '2.3.0'
        mock_validation_args.return_value.arch = 'x64'
        mock_validation_args.return_value.platforms = 'linux'
        mock_validation_args.return_value.allow_without_security = True
        mock_validation_args.return_value.projects = ["opensearch", "opensearch-dashboards"]

        validate_deb = ValidateDeb(mock_validation_args.return_value)
        result = validate_deb.start_cluster()
        self.assertTrue(result)
        mock_execute.assert_has_calls([(('sudo systemctl enable opensearch', "."), {}),
                                       (('sudo systemctl start opensearch', "."), {}),
                                       (('sudo systemctl status opensearch', "."), {}),
                                       (('sudo systemctl enable opensearch-dashboards', "."), {}),
                                       (('sudo systemctl start opensearch-dashboards', "."), {}),
                                       (('sudo systemctl status opensearch-dashboards', "."), {})
                                       ])

    @patch('validation_workflow.deb.validation_deb.execute')
    @patch('validation_workflow.deb.validation_deb.ValidationArgs')
    @patch('time.sleep')
    def test_start_cluster_exception_os(self, mock_sleep: Mock, mock_validation_args: Mock, mock_execute: MagicMock) -> None:
        mock_validation_args.return_value.projects = ["opensearch"]
        mock_validation_args.return_value.allow_without_security = True

        validate_deb = ValidateDeb(mock_validation_args.return_value)
        mock_execute.side_effect = Exception('any exception occurred')
        with self.assertRaises(Exception) as context:
            validate_deb.start_cluster()

        self.assertEqual(str(context.exception), 'Failed to Start Cluster')