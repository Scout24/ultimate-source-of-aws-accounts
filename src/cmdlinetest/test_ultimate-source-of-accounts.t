#!/usr/bin/env cram
# vim: set syntax=cram :

# Test help

  $ ultimate-source-of-accounts -h
  Tool to upload/check a list of your AWS accounts to an S3 bucket
  
  Usage:
      ultimate-source-of-accounts --import=<data-directory> [--allowed-ip=<IP>...] <destination-bucket-name> [--verbose]
      ultimate-source-of-accounts --check-billing=<billing-bucket-name> <destination-bucket-name> [--verbose]
  
  Options:
    -h --help                             Show this.
    --allowed-ip=IP                       IP with access to the destination bucket, can be used multiple times
    --check-billing=<billing-bucket-name> Check Billing account
    -v --verbose                          Log more stuff
    --import=<data-directory>             Import account list from directory
    <destination-bucket-name>             Target bucket
  
  [1]

 Return code must not be 0 when some error occurs.
  $ ultimate-source-of-accounts --import=/directory/that/does/not/exist test_bucket 2>/dev/null
  [1]

 Return code must not be 0 when invalid options are used
  $ ultimate-source-of-accounts --invalid --options --must --be-errors >/dev/null 2>/dev/null
  [1]
