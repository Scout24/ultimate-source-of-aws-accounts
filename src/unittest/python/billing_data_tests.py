# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
from unittest2 import TestCase

import ultimate_source_of_accounts.billing_data as bd


class BillingDataTest(TestCase):

    def test_read_xml_and_return_account_ids(self):
        result = bd.read_xml_and_return_account_ids("foo")
