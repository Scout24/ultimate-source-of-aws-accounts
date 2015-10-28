# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

import os
import shutil
import tempfile

import moto
from mock import patch, Mock
from unittest2 import TestCase

import ultimate_source_of_accounts.cli as cli

class UploadTest(TestCase):
    """Test the upload() function that is used for --import=...."""
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.arguments = {'<destination-bucket-name>': "bucketname42",
            '--allowed-ip': ["123", "345"],
            '--import': self.tempdir,
            '--check-billing': None}

        with open(os.path.join(self.tempdir, "foo.yaml"), "w") as config:
            config.write("my_account:\n  id: 42\n  email: me@host.invalid")

    def tearDown(self):
        shutil.rmtree(self.tempdir)


    @patch("ultimate_source_of_accounts.cli.get_converted_aws_accounts")
    @patch("ultimate_source_of_accounts.cli.S3Uploader")
    def test_upload_loads_data_from_specified_directory(self, mock_exporter_class, mock_converter):
        mock_converter.return_value = {"foo": "bar"}

        cli._main(self.arguments)

        mock_converter.assert_called_once_with({'my_account': {'id': 42, 'email': 'me@host.invalid'}})

    @patch("ultimate_source_of_accounts.cli.get_converted_aws_accounts")
    @patch("ultimate_source_of_accounts.cli.S3Uploader")
    def test_upload_calls_all_upload_tasks(self, mock_exporter_class, mock_converter):
        """Mock away S3 Uploader, see if all necessary methods were called"""
        mock_converter.return_value = {"foo": "bar"}

        mock_exporter_instance = Mock()
        mock_exporter_class.return_value = mock_exporter_instance

        cli._main(self.arguments)

        mock_exporter_class.assert_called_once_with(
                "bucketname42",
                allowed_ips=["123", "345"],
                allowed_aws_account_ids=[42])

        mock_exporter_instance.create_S3_bucket.assert_called_once_with()
        mock_exporter_instance.upload_to_S3.assert_called_once_with({'foo': 'bar'})
        mock_exporter_instance.set_S3_permissions.assert_called_once_with()
        mock_exporter_instance.setup_S3_webserver.assert_called_once_with()

    @patch("ultimate_source_of_accounts.cli.get_converted_aws_accounts")
    @moto.mock_s3
    def test_upload_uses_S3Uploader_correctly(self, mock_converter):
        """Check if the 'necessary methods' used above actually exist on S3Uploader"""
        mock_converter.return_value = {"foo": "bar"}

        cli._main(self.arguments)


class CheckTest(TestCase):
    """Test the check_billing() function that is used for --check_billing"""
    def test_check_billing_not_yet_implemented(self):
        self.assertRaises(SystemExit, cli.check_billing, "foo", "bar")

