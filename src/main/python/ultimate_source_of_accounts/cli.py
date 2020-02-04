# -*- coding: utf-8 -*-


"""
Tool to upload/check a list of your AWS accounts to an S3 bucket

Usage:
    ultimate-source-of-accounts --import=<data-directory> [--organization-id=<ORG_ID>...] [--allowed-ip=<IP>...]
    <destination-bucket-name> [--verbose]
    ultimate-source-of-accounts --check-billing=<billing-bucket-name> <destination-bucket-name> [--verbose]

Options:
  -h --help                             Show this.
  --allowed-ip=IP                       IP with access to the destination bucket, can be used multiple times
  --organization-id=ORG_ID              AWS Org ID to add to policies instead of individual account IDs, can be used multiple times
  --check-billing=<billing-bucket-name> Check Billing account
  -v --verbose                          Log more stuff
  --import=<data-directory>             Import account list from directory
  <destination-bucket-name>             Target bucket
"""

from __future__ import print_function, absolute_import, division

import sys
import logging
from docopt import docopt

from ultimate_source_of_accounts.account_importer import read_directory
from ultimate_source_of_accounts.account_converter import get_converted_aws_accounts
from ultimate_source_of_accounts.account_exporter import S3Uploader


def check_billing(billing_bucket_name, destination_bucket_name):
    print("This feature is not yet implemented.")
    sys.exit(1)


def upload(data_directory, destination_bucket_name, allowed_ips=None, allowed_organization_ids=None):
    allowed_ips = allowed_ips or []

    try:
        account_data = read_directory(data_directory)
    except Exception as e:
        raise Exception("Failed to read data directory '{0}': {1} ".format(data_directory, e))

    data_to_upload = get_converted_aws_accounts(account_data)

    our_account_ids = [account['id'] for account in account_data.values()]
    uploader = S3Uploader(destination_bucket_name,
                          allowed_ips=allowed_ips,
                          allowed_aws_account_ids=our_account_ids,
                          allowed_organization_ids=allowed_organization_ids)

    uploader.setup_infrastructure()
    uploader.upload_to_S3(data_to_upload)


def _main(arguments):
    if arguments['--check-billing']:
        billing_bucket_name = arguments['--check-billing']
        destination_bucket_name = arguments['<destination-bucket-name>']
        check_billing(billing_bucket_name, destination_bucket_name)
    else:
        try:
            allowed_ips = arguments['--allowed-ip']
            organization_ids = arguments.get('--organization-id')
            data_directory = arguments['--import']
            destination_bucket_name = arguments['<destination-bucket-name>']
            upload(data_directory, destination_bucket_name, allowed_ips=allowed_ips,
                   allowed_organization_ids=organization_ids)
        except Exception:
            logging.exception("Failed to upload data: ")
            raise


def main():
    try:
        arguments = docopt(__doc__)
    except SystemExit as exc:
        print(exc)
        sys.exit(1)

    log_level = logging.DEBUG if arguments["--verbose"] else logging.INFO
    logging.basicConfig(format="%(asctime)-15s %(message)s", level=log_level)
    _main(arguments)
