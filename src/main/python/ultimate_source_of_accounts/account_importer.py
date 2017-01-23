# -*- coding: utf-8 -*-
"""Read yaml files with AWS account information and run a consistency check"""

from __future__ import print_function, absolute_import, division

import yamlreader
import logging
import six
from mock import patch


def read_directory(yaml_path):
    """Read yaml files and return merged yaml data"""
    accounts = yamlreader.yaml_load(yaml_path)

    for account in accounts.values():
        account['id'] = str(account['id'])
    _check_account_data(accounts)
    _check_duplicate_account_names(yaml_path)

    logging.debug("Read yaml files from directory '%s'", yaml_path)

    return accounts


# data_merge is patched to get access to the data from each individual
# file, before data is merged. This allows detecting if the same account
# name (not id!) is defined twice, e.g. due to a copy & paste mistake.
@patch("yamlreader.yamlreader.data_merge")
def _check_duplicate_account_names(yaml_path, mock_data_merge):
    yamlreader.yaml_load(yaml_path)
    account_names_found = set()
    for args, kwargs in mock_data_merge.call_args_list:
        _, new_data = args
        names = new_data.keys()
        for name in names:
            if name in account_names_found:
                raise Exception("Duplicate definition of account %r" % name)
            account_names_found.add(name)


def _check_account_data(accounts):
    """Raise exception if account data looks wrong, otherwise return True"""
    if not accounts:
        raise Exception("Account data is empty.")

    all_account_ids = set()
    for account_name, account_data in accounts.items():
        account_id = account_data.get("id")
        if account_id in all_account_ids:
            raise Exception("duplicated id {0} found".format(account_id))
        all_account_ids.add(account_id)
        if not account_data.get("email"):
            raise Exception("Account data {0} has no email.".format(account_name))
        if "@" not in account_data.get("email"):
            raise Exception("Account data {0} without @ in email.".format(account_name))
        if not account_id:
            raise Exception("Account data {0} has no account id.".format(account_name))
        if 'owner' not in account_data:
            raise Exception("Account {0} has no 'owner' field".format(account_name))
        owner = account_data['owner']
        if not isinstance(owner, six.string_types):
            raise Exception("'owner' field of account {0} is not a string.".format(account_name))
        if owner == "":
            raise Exception("'owner' field of account {0} is empty.".format(account_name))

        if "automated" in account_data:
            automated = account_data['automated']
            if not isinstance(automated, dict):
                raise Exception("'automated' field of account {0} is not a dict.".format(account_name))
            for key, value in automated.items():
                if not isinstance(key, six.string_types):
                    raise Exception(
                        "{account_name}.automated may only contain strings, "
                        "but the key '{key}' is of type {key_type}".format(
                            account_name=account_name, key=key, key_type=type(key)))
                if value not in (True, False):
                    raise Exception(
                        "{account_name}.automated.{key} must be boolean, "
                        "but '{value}' is a {value_type}.".format(
                            account_name=account_name, key=key, value=value,
                            value_type=type(value)))
