#!/usr/bin/env cram
# vim: set syntax=cram :

# Test help

  $ ultimate-source-of-accounts -h
  Usage:
      ultimate-source-of-accounts [--allowed-ips=(<IP>,...)]
                                  [--check-billing=<billing-bucket-name>|--import=<data-directory>]
                                  <destination-bucket-name>

  Options:
    -h --help                             Show this.
    --allowed-ips=(<IP>,...)              List of IPs with access to the target bucket
    --check-billing=<billing-bucket-name> Check Billing account
    --import=<data-directory>             Import account list from directory
    <destination-bucket-name>             Target bucket
