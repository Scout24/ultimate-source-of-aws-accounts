# -*- coding: utf-8 -*-


"""
Tool to upload/check a list of your AWS accounts to an S3 bucket

Usage:
    ultimate-source-of-accounts --import=<data-directory> [--allowed-ip=<IP>...] <destination-bucket-name>
    ultimate-source-of-accounts --check-billing=<billing-bucket-name> <destination-bucket-name>

Options:
  -h --help                             Show this.
  --allowed-ip=IP                       IP with access to the destination bucket, can be used multiple times
  --check-billing=<billing-bucket-name> Check Billing account
  --import=<data-directory>             Import account list from directory
  <destination-bucket-name>             Target bucket
"""

from __future__ import print_function, absolute_import, division

import sys
from docopt import docopt

from ultimate_source_of_accounts.account_importer import read_directory
from ultimate_source_of_accounts.account_converter import get_converted_aws_accounts
from ultimate_source_of_accounts.account_exporter import S3Uploader


def check_billing(billing_bucket_name, destination_bucket_name):
    print("This feature is not yet implemented.")
    sys.exit(1)


def upload(data_directory, destination_bucket_name, allowed_ips=None):
    allowed_ips = allowed_ips or []

    account_data = read_directory(data_directory)
    data_to_upload = get_converted_aws_accounts(account_data)

    our_account_ids = [account['id'] for account in account_data.values()]
    # TODO: do we need the writer arn?
    uploader = S3Uploader(destination_bucket_name, 'some-random-writer-arn',
                          allowed_ips=allowed_ips,
                          allowed_aws_account_ids=our_account_ids)


    uploader.create_bucket()
    uploader.set_S3_permission()
    uploader.upload_to_S3(data_to_upload)
    uploader.setup_S3_webserver()

def _main(arguments):
    if arguments['--check-billing']:
        billing_bucket_name = arguments['--check-billing']
        destination_bucket_name = arguments['<destination-bucket-name>']
        check_billing(billing_bucket_name, destination_bucket_name)
    else:
        allowed_ips = arguments['--allowed-ip']
        data_directory = arguments['--import']
        destination_bucket_name = arguments['<destination-bucket-name>']
        upload(data_directory, destination_bucket_name, allowed_ips=allowed_ips)


def main():
    arguments = docopt(__doc__)
    _main(arguments)

