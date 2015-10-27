#!/usr/bin/env cram
# vim: set syntax=cram :

# Test help

  $ ultimate-source-of-accounts -h
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


