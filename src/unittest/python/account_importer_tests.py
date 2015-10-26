# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
from mock import patch
from unittest2 import TestCase
import tempfile
import shutil
import os
import yaml

import ultimate_source_of_accounts.account_importer as ai


class AccountImportTest(TestCase):
    def test_raise_exception_when_account_data_empty(self):
        account_data = {}
        self.assertRaises(Exception, ai._check_account_data, account_data)

    def test_raise_exception_when_account_data_without_email(self):
        account_data = {"account_name": {"id": 42, "email": ""}}
        self.assertRaises(Exception, ai._check_account_data, account_data)

        account_data = {"account_name": {"id": 42}}
        self.assertRaises(Exception, ai._check_account_data, account_data)

    def test_raise_exception_when_account_data_with_invalid_email(self):
        account_data = {"account_name": {"id": 42, "email": "test.testqtest.test"}}
        self.assertRaises(Exception, ai._check_account_data, account_data)

    def test_raise_exception_when_account_data_without_account_id(self):
        account_data = {"account_name": {"email": "test.test@test.test"}}
        self.assertRaises(Exception, ai._check_account_data, account_data)

    def test_raise_exception_when_account_data_without_account_id_and_email(self):
        account_data = {"account_name": {}}
        self.assertRaises(Exception, ai._check_account_data, account_data)

    def test_accept_valid_data(self):
        account_data = {"account_name1": {"id": 42, "email": "test.test@test.test"}}
        ai._check_account_data(account_data)

    @patch("ultimate_source_of_accounts.account_importer._check_account_data")
    def test_loaded_data_is_checked(self, mock_check_account):
        directory = tempfile.mkdtemp()
        filename = "account.yaml"
        content = "ab42"

        try:
            with open(os.path.join(directory, filename), "w") as test_file:
                test_file.write(content)

            ai.read_directory(directory)

            mock_check_account.assert_called_once_with(content)
        finally:
            shutil.rmtree(directory)

    def test_loaded_data_is_returned_data(self):
        directory = tempfile.mkdtemp()
        filename = "account.yaml"
        content = {"account_name": {"id": 42, "email": "test.test@test.test"}}

        try:
            with open(os.path.join(directory, filename), "w") as test_file:
                test_file.write(yaml.dump(content))

            result = ai.read_directory(directory)

            self.assertEqual(content, result)
        finally:
            shutil.rmtree(directory)

    def test_raise_exception_when_account_has_the_same_account_id(self):
        account_data = {"account_name1": {"id": 42, "email": "test.test@test.test"},
                        "account_name2": {"id": 42, "email": "test2.test2@test.test"}}

        self.assertRaises(Exception, ai._check_account_data, account_data)

    def test_raise_exception_when_two_accounts_have_same_account_id(self):
        account_data = {"account_name1": {"id": 42, "email": "test.test@test.test"},
                        "account_name2": {"id": 43, "email": "test2.test2@test.test"},
                        "account_name3": {"id": 42, "email": "test3.test2@test.test"},
                        "account_name4": {"id": 43, "email": "test2.test2@test.test"}}

        self.assertRaises(Exception, ai._check_account_data, account_data)

    def test_accounts_with_different_ids(self):
        account_data = {"account_name1": {"id": 42, "email": "test.test@test.test"},
                        "account_name2": {"id": 43, "email": "test2.test2@test.test"}}
        ai._check_account_data(account_data)

