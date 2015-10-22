# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
from unittest2 import TestCase

import ultimate_source_of_accounts.account_converter as ac

class AccountConverterTest(TestCase):

    def test_raise_exception_when_account_data_is_empty(self):
        account_data = {}
        self.assertRaises(Exception, ac.get_converted_aws_accounts, account_data)

    def test_return_accounts_as_yaml_when_account_data_is_valid(self):
        account_data = {"account_name1": {"id": 42, "email": "test.test@test.test"},
                        "account_name2": {"id": 43, "email": "täst.test@test.test"}}
