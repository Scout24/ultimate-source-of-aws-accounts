# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
from unittest2 import TestCase
from moto import mock_s3
import boto
import json
import os
import time

import ultimate_source_of_accounts.account_exporter as ae

BUCKET_REGION = "us-west-2"

# Else we run into problems with mocking
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['no_proxy'] = ''


class AccountExporterTest(TestCase):
    @mock_s3
    def setUp(self):
        self.old_bucket_region = ae.BUCKET_REGION
        ae.BUCKET_REGION = BUCKET_REGION
        self.bucket_name = "testbucket"
        self.allowed_ips = ["123.131.124.5"]
        self.allowed_aws_account_ids = ["123456789"]

        self.s3_uploader = ae.S3Uploader(self.bucket_name,
                                         allowed_ips=self.allowed_ips,
                                         allowed_aws_account_ids=self.allowed_aws_account_ids)

    @mock_s3
    def test_create_S3_bucket_if_bucket_not_exists(self):
        conn = boto.s3.connect_to_region(BUCKET_REGION)

        self.s3_uploader.create_S3_bucket()

        bucket = conn.get_bucket(self.bucket_name)

        self.assertEqual(list(bucket.list()), [])

    @mock_s3
    def test_create_S3_bucket_if_bucket_exists(self):
        conn = boto.s3.connect_to_region(BUCKET_REGION)
        conn.create_bucket(self.bucket_name)

        self.s3_uploader.create_S3_bucket()

    @mock_s3
    def test_create_S3_bucket_must_not_delete_data(self):
        conn = boto.s3.connect_to_region(BUCKET_REGION)
        conn.create_bucket(self.bucket_name)
        bucket = conn.get_bucket(self.bucket_name)
        key = boto.s3.key.Key(bucket)
        key.key = "foobar"
        key.set_contents_from_string('This is a test of USofA')

        self.s3_uploader.create_S3_bucket()

        key = boto.s3.key.Key(bucket)
        key.key = "foobar"
        result = key.get_contents_as_string(encoding="utf-8")

        self.assertEqual('This is a test of USofA', result)

    @mock_s3
    def test_create_S3_bucket_and_test_is_the_location_EU(self):
        conn = boto.s3.connect_to_region(BUCKET_REGION)

        self.s3_uploader.create_S3_bucket()

        bucket = conn.get_bucket(self.bucket_name)

        self.assertEqual(BUCKET_REGION, bucket.get_location())

    @mock_s3
    def test_upload_to_S3(self):
        conn = boto.s3.connect_to_region(BUCKET_REGION)
        conn.create_bucket(self.bucket_name)

        upload_data = {"foo": "bar"}

        self.s3_uploader.upload_to_S3(upload_data)

        bucket = conn.get_bucket(self.bucket_name)
        key = boto.s3.key.Key(bucket)
        key.key = bucket.get_key("foo")

        result = key.get_contents_as_string(encoding="utf-8")

        self.assertEqual(result, "bar")

    @mock_s3
    def test_set_permissions_for_s3_bucket(self):
        conn = boto.s3.connect_to_region(BUCKET_REGION)
        conn.create_bucket(self.bucket_name)
        expected_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Action": [
                    "s3:GetBucketWebsite",
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Effect": "Allow",
                "Resource": [
                    "arn:aws:s3:::{0}/*".format(self.bucket_name),
                    "arn:aws:s3:::{0}".format(self.bucket_name)
                ],
                "Principal": {
                    "AWS": self.allowed_aws_account_ids
                }
            },
                {
                    "Action": [
                        "s3:GetBucketWebsite",
                        "s3:GetObject",
                        "s3:ListBucket"
                    ],
                    "Effect": "Allow",
                    "Resource": [
                        "arn:aws:s3:::{0}/*".format(self.bucket_name),
                        "arn:aws:s3:::{0}".format(self.bucket_name)
                    ],
                    "Condition": {
                        "IpAddress": {
                            "aws:SourceIp": self.allowed_ips
                        }
                    },
                    "Principal": {
                        "AWS": "*"
                    }
                }
            ]
        }

        self.s3_uploader.set_S3_permissions()
        bucket = conn.get_bucket(self.bucket_name)
        policy = bucket.get_policy().decode("utf-8")

        self.assertEqual(expected_policy, json.loads(policy))

    @mock_s3
    def test_setup_S3_webserver(self):
        upload_data = {"foo": "bar"}
        conn = boto.s3.connect_to_region(BUCKET_REGION)

        # self.s3_uploader.create_S3_bucket()
        self.s3_uploader.set_S3_permissions()
        self.s3_uploader.upload_to_S3(upload_data)
        self.s3_uploader.setup_S3_webserver()

        # wait until the settings applied
        time.sleep(5)
        bucket = conn.get_bucket(self.bucket_name)
        # now get the website configuration, just to check it
        print(bucket.get_website_configuration())
