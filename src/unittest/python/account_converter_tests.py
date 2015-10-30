# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
from unittest2 import TestCase
from mock import patch
import yaml
import json

import ultimate_source_of_accounts.account_converter as ac


class AccountConverterTest(TestCase):

    def test_return_accounts_as_yaml_when_account_data_is_valid(self):
        account_data = {"account_name1": {"id": 42, "email": "test.test@test.test"}}

        result = ac.get_converted_aws_accounts(account_data)
        yaml_result = result["accounts.yaml"]
        decoded_result = yaml.safe_load(yaml_result)

        self.assertEqual(decoded_result, account_data)

    def test_return_accounts_as_json_when_account_data_is_valid(self):
        account_data = {"account_name1": {"id": 42, "email": "test.test@test.test"}}

        result = ac.get_converted_aws_accounts(account_data)
        json_result = result["accounts.json"]
        decoded_result = json.loads(json_result)

        self.assertEqual(decoded_result, account_data)

    @patch("ultimate_source_of_accounts.account_converter.json.dumps")
    def test_raise_exception_when_json_convert_failed(self, json_dump_mock):
        account_data = {"account_name1": {"id": 42, "email": "test.test@test.test"}}

        json_dump_mock.side_effect = Exception("Failed to convert")

        self.assertRaises(Exception, ac.get_converted_aws_accounts, account_data)

    @patch("ultimate_source_of_accounts.account_converter.yaml.dump")
    def test_raise_exception_when_yaml_convert_failed(self, yaml_dump_mock):
        account_data = {"account_name1": {"id": 42, "email": "test.test@test.test"}}

        yaml_dump_mock.side_effect = Exception("Failed to convert")

        self.assertRaises(Exception, ac.get_converted_aws_accounts, account_data)