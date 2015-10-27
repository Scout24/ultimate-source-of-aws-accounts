# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
from unittest2 import TestCase
import yaml
import json

import ultimate_source_of_accounts.account_converter as ac


class AccountConverterTest(TestCase):

    def test_return_accounts_as_yaml_when_account_data_is_valid(self):
        account_data = {"account_name1": {"id": 42, "email": "test.test@test.test"}}

        result = ac.get_converted_aws_accounts(account_data)
        yaml_result = result["usofa.yaml"]
        decoded_result = yaml.safe_load(yaml_result)

        self.assertEqual(decoded_result, account_data)

    def test_return_accounts_as_json_when_account_data_is_valid(self):
        account_data = {"account_name1": {"id": 42, "email": "test.test@test.test"}}

        result = ac.get_converted_aws_accounts(account_data)
        json_result = result["usofa.json"]
        decoded_result = json.loads(json_result)

        self.assertEqual(decoded_result, account_data)
