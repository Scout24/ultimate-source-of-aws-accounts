# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

import yamlreader


""" This module read yaml files with AWS account information and can execute a consistency check """


def read_directory(yaml_path):
    """ Read yaml files and return merged yaml files """
    accounts = yamlreader.yaml_load(yaml_path)
    _check_account_data(accounts)

    return accounts


def _check_account_data(accounts):
    """ Raise exception if account data looks wrong otherwise return true"""
    if not accounts:
        raise Exception("Account data is empty.")

    for account_name, account_data in accounts.items():
        if not account_data.get("email"):
            raise Exception("Account data {0} has no email.".format(account_name))
        if "@" not in account_data.get("email"):
            raise Exception("Account data {0} without @ in email.".format(account_name))
        if not account_data.get("id"):
            raise Exception("Account data {0} has no account id.".format(account_name))
