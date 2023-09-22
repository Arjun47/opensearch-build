import unittest
from unittest.mock import Mock, patch
import logging

from validation_workflow.validation_args import ValidationArgs
from validation_workflow.validation import Validation
from validation_workflow.tar.validation_tar import ValidateTar

from system.temporary_directory import TemporaryDirectory


class ImplementValidation(Validation):
    def __init__(self, args: ValidationArgs) -> None:
        super().__init__(args)
        self.tmp_dir = TemporaryDirectory()

    def download_artifacts(self):
        return True
    def installation(self):
        return True
    def start_cluster(self):
        return True
    def validation(self):
        return True
    def cleanup(self):
        return True

class TestValidation(unittest.TestCase):

    @patch('validation_workflow.download_utils.DownloadUtils.is_url_valid')
    @patch('validation_workflow.tar.validation_tar.ValidationArgs')
    def test_check_url_valid(self, mock_validation_args: Mock, mock_download_utils: Mock):
        mock_validation_args.projects.return_value = ["opensearch"]

        mock_validation = ValidateTar(mock_validation_args.return_value)
        mock_download_utils_download = mock_download_utils.return_value
        mock_download_utils_download.download.return_value = False
        mock_download_utils_download.is_url_valid.return_value = False


        url = "https://ci.opensearch.org/ci/dbc/distribution-build-opensearch/1.3.12/latest/linux/x64/rpm/dist/opensearch/opensearch-1.3.12.staging.repo"

        result = mock_validation.check_url(url)
        self.assertTrue(result)



