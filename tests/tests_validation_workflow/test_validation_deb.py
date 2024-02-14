# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import unittest
from unittest.mock import MagicMock, Mock, patch, call

from system.process import Process
from validation_workflow.deb.validation_deb import ValidateDeb


class TestValidateDeb(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_args = MagicMock()
        self.mock_args.version = "2.3.0"
        self.mock_args.arch = "x64"
        self.mock_args.projects = ["opensearch"]
        self.mock_args.file_path = {"opensearch": "/src/opensearch/opensearch-1.3.12.staging.deb"}
        self.mock_args.platform = "linux"
        self.mock_args.force_https_check = True
        self.mock_args.allow_without_security = True
        self.call_methods = ValidateDeb(self.mock_args)

    @patch("time.sleep")
    @patch("validation_workflow.deb.validation_deb.ValidationArgs")
    @patch("validation_workflow.deb.validation_deb.execute")
    @patch("validation_workflow.deb.validation_deb.get_password")
    def test_installation(
            self, mock_get_pwd: Mock, mock_system: Mock, mock_validation_args: Mock, mock_sleep: Mock
    ) -> None:
        validate_deb = ValidateDeb(self.mock_args)
        mock_system.side_effect = lambda *args, **kwargs: (0, "stdout_output", "stderr_output")
        result = validate_deb.installation()
        self.assertTrue(result)
        mock_get_pwd.assert_called_with("2.3.0")

    @patch("time.sleep")
    @patch("validation_workflow.deb.validation_deb.ValidationArgs")
    @patch("validation_workflow.deb.validation_deb.execute")
    @patch("validation_workflow.deb.validation_deb.get_password")
    def test_installation_exception_os(
            self, mock_get_pwd: Mock, mock_execute: Mock, mock_validation_args: Mock, mock_sleep: Mock
    ) -> None:
        validate_deb = ValidateDeb(self.mock_args)
        mock_execute.side_effect = Exception("any exception occurred")
        with self.assertRaises(Exception) as context:
            validate_deb.installation()

        mock_get_pwd.assert_called_with("2.3.0")
        self.assertEqual(str(context.exception), "Failed to install Opensearch")

    @patch("validation_workflow.deb.validation_deb.execute")
    @patch("validation_workflow.deb.validation_deb.ValidationArgs")
    @patch("time.sleep")
    def test_start_cluster(self, mock_sleep: Mock, mock_validation_args: Mock, mock_execute: Mock) -> None:
        self.mock_args.projects = ["opensearch", "opensearch-dashboards"]

        validate_deb = ValidateDeb(self.mock_args)
        result = validate_deb.start_cluster()
        self.assertTrue(result)
        mock_execute.assert_has_calls(
            [
                call("sudo systemctl enable opensearch", "."),
                call("sudo systemctl start opensearch", "."),
                call("sudo systemctl status opensearch", "."),
                call("sudo systemctl enable opensearch-dashboards", "."),
                call("sudo systemctl start opensearch-dashboards", "."),
                call("sudo systemctl status opensearch-dashboards", "."),
            ]
        )

    @patch("validation_workflow.deb.validation_deb.execute")
    @patch("validation_workflow.deb.validation_deb.ValidationArgs")
    @patch("time.sleep")
    def test_start_cluster_exception_os(
            self, mock_sleep: Mock, mock_validation_args: Mock, mock_execute: MagicMock
    ) -> None:
        validate_deb = ValidateDeb(self.mock_args)
        mock_execute.side_effect = Exception("any exception occurred")
        with self.assertRaises(Exception) as context:
            validate_deb.start_cluster()

        self.assertEqual(str(context.exception), "Failed to Start Cluster")

    @patch("validation_workflow.deb.validation_deb.ValidationArgs")
    @patch("validation_workflow.deb.validation_deb.ApiTestCases")
    @patch("validation_workflow.validation.Validation.check_for_security_plugin")
    def test_validation(self, mock_security: Mock, mock_test_apis: Mock, mock_validation_args: Mock) -> None:
        mock_test_apis_instance = mock_test_apis.return_value
        mock_test_apis_instance.test_apis.return_value = (True, 3)

        validate_deb = ValidateDeb(self.mock_args)

        result = validate_deb.validation()
        self.assertTrue(result)

        mock_test_apis.assert_called_once()
        mock_security.assert_not_called()

    @patch("validation_workflow.deb.validation_deb.ValidationArgs")
    @patch("validation_workflow.deb.validation_deb.ApiTestCases")
    @patch("validation_workflow.validation.Validation.check_for_security_plugin")
    def test_validation_without_force_https_check(
            self, mock_security: Mock, mock_test_apis: Mock, mock_validation_args: Mock
    ) -> None:
        self.mock_args.force_https = False
        validate_deb = ValidateDeb(self.mock_args)
        mock_test_apis_instance = mock_test_apis.return_value
        mock_test_apis_instance.test_apis.return_value = (True, 4)

        result = validate_deb.validation()
        self.assertTrue(result)
        mock_security.assert_called_once()

    @patch("validation_workflow.deb.validation_deb.ValidationArgs")
    @patch("validation_workflow.deb.validation_deb.ApiTestCases")
    def test_failed_testcases(self, mock_test_apis: Mock, mock_validation_args: Mock) -> None:
        mock_test_apis_instance = mock_test_apis.return_value
        mock_test_apis_instance.test_apis.return_value = (False, 1)

        # Create instance of ValidateDeb class
        validate_deb = ValidateDeb(self.mock_args)

        # Call validation method and assert the result
        with self.assertRaises(Exception) as context:
            validate_deb.validation()

        self.assertEqual(str(context.exception), "Not all tests Pass : 1")

        # Assert that the mock methods are called as expected
        mock_test_apis.assert_called_once()

    @patch("validation_workflow.deb.validation_deb.ValidationArgs")
    @patch("validation_workflow.deb.validation_deb.execute")
    def test_cleanup(self, mock_execute: Mock, mock_validation_args: Mock) -> None:
        self.mock_args.projects = ["opensearch", "opensearch-dashboards"]

        validate_deb = ValidateDeb(self.mock_args)
        result = validate_deb.cleanup()
        self.assertTrue(result)
        mock_execute.assert_has_calls(
            [call("sudo dpkg --purge opensearch", "."), call("sudo dpkg --purge opensearch-dashboards", ".")]
        )

    @patch("validation_workflow.deb.validation_deb.ValidationArgs")
    @patch("validation_workflow.deb.validation_deb.execute")
    def test_cleanup_exception(self, mock_execute: Mock, mock_validation_args: Mock) -> None:
        self.mock_args.projects = ["opensearch", "opensearch-dashboards"]
        mock_execute.side_effect = Exception("an exception occurred")
        validate_deb = ValidateDeb(self.mock_args)
        with self.assertRaises(Exception) as context:
            validate_deb.cleanup()

        self.assertEqual(
            str(context.exception),
            "Exception occurred either while attempting to stop cluster or removing OpenSearch/OpenSearch-Dashboards. an exception occurred",
        )
