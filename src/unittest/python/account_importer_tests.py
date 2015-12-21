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
        account_data = {"account_name": {"id": "42", "email": ""}}
        self.assertRaises(Exception, ai._check_account_data, account_data)

        account_data = {"account_name": {"id": "42"}}
        self.assertRaises(Exception, ai._check_account_data, account_data)

    def test_raise_exception_when_account_data_with_invalid_email(self):
        account_data = {"account_name": {"id": "42", "email": "test.testqtest.test"}}
        self.assertRaises(Exception, ai._check_account_data, account_data)

    def test_raise_exception_when_account_data_without_account_id(self):
        account_data = {"account_name": {"email": "test.test@test.test"}}
        self.assertRaises(Exception, ai._check_account_data, account_data)

    def test_raise_exception_when_account_data_without_account_id_and_email(self):
        account_data = {"account_name": {}}
        self.assertRaises(Exception, ai._check_account_data, account_data)

    def test_raise_exception_when_account_data_without_owner(self):
        account_data = {
            "account_name1": {"id": "42", "email": "test.test@test.test"}}
        self.assertRaises(Exception, ai._check_account_data, account_data)

    def test_raise_exception_when_account_data_with_invalid_owner(self):
        account_data = {
            "account_name1": {"id": "42", "email": "test.test@test.test"}}
        for invalid_owner in (True, 42, ""):
            account_data['account_name1']['owner'] = invalid_owner
            self.assertRaises(Exception, ai._check_account_data, account_data)

    def test_accept_valid_data(self):
        account_data = {
            "account_name1": {
                "id": "42",
                "email": "test.test@test.test",
                "owner": "me"}}
        ai._check_account_data(account_data)

    def test_account_id_is_converted_to_string(self):
        directory = tempfile.mkdtemp()
        filename = "account.yaml"
        content = {
            "account_name": {"id": 42, "email": "test.test@test.test", "owner": "me"},
            "another": {"id": "43", "email": "test.test@test.test", "owner": "minime"}}

        try:
            with open(os.path.join(directory, filename), "w") as test_file:
                test_file.write(yaml.dump(content))

            result = ai.read_directory(directory)

            expected_content = content
            # Must have been converted from int 42 to string "42".
            expected_content['account_name']['id'] = '42'
            self.assertEqual(expected_content, result)
        finally:
            shutil.rmtree(directory)


    @patch("ultimate_source_of_accounts.account_importer._check_account_data")
    def test_loaded_data_is_checked(self, mock_check_account):
        directory = tempfile.mkdtemp()
        filename = "account.yaml"
        content = "account_one:\n  id: 1\n  email: one@s24.de\n  owner: me"

        try:
            with open(os.path.join(directory, filename), "w") as test_file:
                test_file.write(content)

            ai.read_directory(directory)

            mock_check_account.assert_called_once_with(
                {'account_one': {
                    'id': '1', 'email': 'one@s24.de', 'owner': 'me'}})
        finally:
            shutil.rmtree(directory)

    def test_loaded_data_is_returned_data(self):
        directory = tempfile.mkdtemp()
        filename = "account.yaml"
        content = {"account_name": {"id": "42", "email": "test.test@test.test", "owner": "me"}}

        try:
            with open(os.path.join(directory, filename), "w") as test_file:
                test_file.write(yaml.dump(content))

            result = ai.read_directory(directory)

            self.assertEqual(content, result)
        finally:
            shutil.rmtree(directory)

    def test_raise_exception_when_account_has_the_same_account_id(self):
        directory = tempfile.mkdtemp()
        filename = "account.yaml"
        # Duplicates must be detected even if one item is given as a string,
        # the other as integer.
        content = {"account_name1": {"id": 42, "email": "test.test@test.test", "owner": "me"},
                   "account_name2": {"id": "42", "email": "test2.test2@test.test", "owner": "notme"}}

        try:
            with open(os.path.join(directory, filename), "w") as test_file:
                test_file.write(yaml.dump(content))

            self.assertRaises(Exception, ai.read_directory, directory)
        finally:
            shutil.rmtree(directory)


    def test_raise_exception_when_two_accounts_have_same_account_id(self):
        account_data = {"account_name1": {"id": "42", "email": "test.test@test.test", "owner": "me"},
                        "account_name2": {"id": "43", "email": "test2.test2@test.test", "owner": "me"},
                        "account_name3": {"id": "42", "email": "test3.test2@test.test", "owner": "me"},
                        "account_name4": {"id": "43", "email": "test2.test2@test.test", "owner": "me"}}

        self.assertRaises(Exception, ai._check_account_data, account_data)

    def test_accounts_with_different_ids(self):
        account_data = {"account_name1": {"id": "42", "email": "test.test@test.test", "owner": "me"},
                        "account_name2": {"id": "43", "email": "test2.test2@test.test", "owner": "me"}}
        ai._check_account_data(account_data)


class AutomatedFieldTests(TestCase):
    """Various tests for the 'automated' field in the account data"""
    def setUp(self):
        self.account_data = {
            "account1": {
                "id": "42",
                "email": "test.test@test.test",
                "owner": "me",
                "automated": {}
        }}

    def test_valid_data_is_accepted(self):
        self.account_data['account1']['automated'] = {
            'foo': True,
            'bar': False}
        ai._check_account_data(self.account_data)

    def test_empty_automated_field_is_allowed(self):
        ai._check_account_data(self.account_data)

    def test_omitting_the_automated_field_is_allowed(self):
        del self.account_data['account1']['automated']
        ai._check_account_data(self.account_data)

    def test_raise_exception_when_automated_is_no_dict(self):
        for invalid_automated in (True, 42, "hello", []):
            self.account_data['account1']['automated'] = invalid_automated
            self.assertRaises(Exception, ai._check_account_data, self.account_data)

    def test_raise_exception_when_automated_keys_are_no_strings(self):
        for invalid_key in (True, 42, "", tuple()):
            self.account_data['account1']['automated'][invalid_key] = False
            self.assertRaises(Exception, ai._check_account_data, self.account_data)

    def test_raise_exception_when_automated_values_are_no_bools(self):
        for invalid_value in ("hello", 42, "", []):
            self.account_data['account1']['automated']['foo'] = invalid_value
            self.assertRaises(Exception, ai._check_account_data, self.account_data)
