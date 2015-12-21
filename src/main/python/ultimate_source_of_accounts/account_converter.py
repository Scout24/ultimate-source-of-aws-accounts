# -*- coding: utf-8 -*-
"""Convert AWS account information from internal to external format"""

from __future__ import print_function, absolute_import, division
import yaml
import json
import logging


FILENAME = "accounts"


def get_converted_aws_accounts(accounts):
    """Return converted AWS account data.

    Produces a dictionary of "file name" -> "file content" pairs. When
    uploading to S3, these become "S3 key" -> "S3 value" pairs.
    """

    try:
        result = {
            "{filename}.yaml".format(filename=FILENAME): yaml.dump(accounts),
            "{filename}.json".format(filename=FILENAME): json.dumps(accounts)}
    except Exception as exc:
        raise Exception("Failed to convert to yaml and json: {0}".format(exc))

    logging.debug("Data successfully converted to yaml and json")
    return result
