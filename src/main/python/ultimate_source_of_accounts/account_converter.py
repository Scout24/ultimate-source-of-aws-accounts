# -*- coding: utf-8 -*-
"""Convert AWS account information from internal to external format"""

from __future__ import print_function, absolute_import, division
import yaml
import json
import logging


FILENAME = "accounts"


def represent_unicode(dumper, data, style=None):
    if not dumper.default_style and data.isdigit():
        style = "'"
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style=style)


class MyDumper(yaml.Dumper):
    pass

# Always use quotes when the string contains only digits
MyDumper.add_representer(str, represent_unicode)


def get_converted_aws_accounts(accounts):
    """Return converted AWS account data.

    Produces a dictionary of "file name" -> "file content" pairs. When
    uploading to S3, these become "S3 key" -> "S3 value" pairs.
    """
    try:
        yaml_data = yaml.dump(accounts, indent=2, default_flow_style=False,
                              Dumper=MyDumper)
        json_data = json.dumps(accounts, sort_keys=True, indent=2)
    except Exception as exc:
        raise Exception("Failed to convert to yaml and json: {0}".format(exc))
    logging.debug("Data successfully converted to yaml and json")

    return {FILENAME + ".yaml": yaml_data,
            FILENAME + ".json": json_data}
