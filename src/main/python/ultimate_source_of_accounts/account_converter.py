# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
import yaml
import json

""" This module export AWS account information (account id, account name, account email) into an file. """


def get_converted_aws_accounts(accounts):
    """ Return converted AWS account data """

    return {
        "usofa.yaml": yaml.dump(accounts),
        "usofa.json": json.dumps(accounts)
        }
