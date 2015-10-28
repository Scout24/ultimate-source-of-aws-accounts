# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
import yaml
import json

""" This module export AWS account information (account id, account name, account email) into an file. """

FILENAME = "accounts"


def get_converted_aws_accounts(accounts):
    """ Return converted AWS account data """

    return {
        "{filename}.yaml".format(filename=FILENAME): yaml.dump(accounts),
        "{filename}.json".format(filename=FILENAME): json.dumps(accounts)
    }
