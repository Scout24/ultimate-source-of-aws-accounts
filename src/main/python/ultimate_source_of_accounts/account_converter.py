# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
import yaml
import json
import logging

""" This module exports AWS account information (account id, account name, account email). """

FILENAME = "accounts"


def get_converted_aws_accounts(accounts):
    """ Return converted AWS account data """

    try:
        result = {"{filename}.yaml".format(filename=FILENAME): yaml.dump(accounts),
                  "{filename}.json".format(filename=FILENAME): json.dumps(accounts)}
    except Exception as e:
        raise Exception("Failed to convert to yaml and json: {0}".format(e))

    logging.debug("Data successfully converted to yaml and json")
    return result
