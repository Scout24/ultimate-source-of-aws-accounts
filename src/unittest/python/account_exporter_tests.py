# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
from unittest2 import TestCase
from moto import mock_s3, mock_sns
import boto
import json
import os
import logging
from mock import Mock

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

        with self.assertLogs(level=logging.DEBUG) as cm:
            self.s3_uploader.create_S3_bucket()
        logged_output = "\n".join(cm.output)
        self.assertIn("Could not create S3 bucket '{0}': ".format(self.bucket_name), logged_output)

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
        mock_bucket = Mock()
        self.s3_uploader.s3_conn.get_bucket = Mock(return_value=mock_bucket)
        self.s3_uploader.get_routing_rules = Mock(return_value='mock_routing_rules')

        self.s3_uploader.setup_S3_webserver()

        routing_rules = self.s3_uploader.get_routing_rules()
        mock_bucket.configure_website.assert_called_once_with(suffix='accounts.json', routing_rules=routing_rules)

    @mock_sns
    def test_create_sns_topic_if_none_existing(self):
        topic_arn = self.s3_uploader.create_sns_topic()
        self.assertIsNotNone(topic_arn)

    @mock_sns
    def test_create_sns_topic_if_already_existing(self):
        response = boto.sns.connect_to_region(BUCKET_REGION).create_topic(self.bucket_name)
        topic_arn = response['CreateTopicResponse']['CreateTopicResult']['TopicArn']

        self.assertEqual(topic_arn, self.s3_uploader.create_sns_topic())

    @mock_sns
    def test_set_topic_policy(self):
        topic_arn = self.s3_uploader.create_sns_topic()
        expected_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "allow_s3_events",
                    "Effect": "Allow",
                    "Action": [
                        "sns:Publish"
                    ],
                    "Principal": {
                        "AWS":"*"
                    },
                    "Resource": topic_arn,
                    "Condition": {
                        "ArnLike": {
                            "aws:SourceArn": "arn:aws:s3:*:*:{0}".format(self.bucket_name)
                        }
                    }
                },{
                    "Sid": "allow_subscribe_to_all_acconts",
                    "Effect": "Allow",
                    "Action": [
                        "sns:Subscribe"
                    ],
                    "Principal": {
                        "AWS": self.allowed_aws_account_ids
                    },
                    "Resource": topic_arn
                }
            ]
        }

        self.s3_uploader.set_sns_topic_policy(topic_arn)
        response = boto.sns.connect_to_region(BUCKET_REGION).get_topic_attributes(topic_arn)
        created_policy = json.loads(
                response['GetTopicAttributesResponse']['GetTopicAttributesResult']['Attributes']['Policy'])

        self.assertEqual(created_policy, expected_policy)
