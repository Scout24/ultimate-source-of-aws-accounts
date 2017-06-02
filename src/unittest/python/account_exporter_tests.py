# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
from unittest2 import TestCase, skip
from moto import mock_s3, mock_sns
import boto3
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
        self.s3_uploader.create_S3_bucket()

        client = boto3.client('s3')
        response = client.list_objects_v2(Bucket=self.bucket_name)
        self.assertEqual(response.get('Contents'), None)

    @skip("Wait for https://github.com/spulec/moto/issues/970 to be fixed")
    @mock_s3
    def test_create_S3_bucket_if_bucket_exists(self):
        client = boto3.client('s3', region_name=BUCKET_REGION)
        client.create_bucket(Bucket=self.bucket_name)

        with self.assertLogs(level=logging.DEBUG) as cm:
            self.s3_uploader.create_S3_bucket()
        logged_output = "\n".join(cm.output)
        self.assertIn("Could not create S3 bucket '{0}': ".format(self.bucket_name), logged_output)

    @mock_s3
    def test_create_S3_bucket_must_not_delete_data(self):
        client = boto3.client('s3', region_name=BUCKET_REGION)

        client.create_bucket(Bucket=self.bucket_name)
        client.put_object(Bucket=self.bucket_name, Key='foobar',
                          Body='This is a test of USofA')

        self.s3_uploader.create_S3_bucket()

        response = client.get_object(Bucket=self.bucket_name, Key='foobar')
        self.assertEqual('This is a test of USofA', response['Body'].read().decode("utf-8"))

    @skip("Wait for https://github.com/spulec/moto/issues/971 to be fixed")
    @mock_s3
    def test_create_S3_bucket_and_test_is_the_location_EU(self):
        client = boto3.client('s3', region_name=BUCKET_REGION)

        self.s3_uploader.create_S3_bucket()

        actual_location = client.get_bucket_location(Bucket=self.bucket_name)['LocationConstraint']
        self.assertEqual(BUCKET_REGION, actual_location)

    @mock_s3
    def test_upload_to_S3(self):
        client = boto3.client('s3', region_name=BUCKET_REGION)
        client.create_bucket(Bucket=self.bucket_name)

        upload_data = {"foo": "bar"}

        self.s3_uploader.upload_to_S3(upload_data)

        response = client.get_object(Bucket=self.bucket_name, Key="foo")
        result = response['Body'].read().decode("utf-8")

        self.assertEqual(result, "bar")

    @mock_s3
    def test_set_permissions_for_s3_bucket(self):
        client = boto3.client('s3', region_name=BUCKET_REGION)
        client.create_bucket(Bucket=self.bucket_name)

        self.s3_uploader.set_S3_permissions()

        actual_policy = client.get_bucket_policy(Bucket=self.bucket_name)['Policy']
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
        self.assertEqual(expected_policy, json.loads(actual_policy))

    @mock_sns
    def test_create_sns_topic_if_none_existing(self):
        topic_arn = self.s3_uploader.create_sns_topic()
        self.assertIsNotNone(topic_arn)

    @mock_sns
    def test_create_sns_topic_if_already_existing(self):
        client = boto3.client('sns', region_name=BUCKET_REGION)
        response = client.create_topic(Name=self.bucket_name)
        expected_topic_arn = response['TopicArn']

        actual_topic_arn = self.s3_uploader.create_sns_topic()

        self.assertEqual(expected_topic_arn, actual_topic_arn)

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

        client = boto3.client('sns', region_name=BUCKET_REGION)
        response = client.get_topic_attributes(TopicArn=topic_arn)
        created_policy = json.loads(response['Attributes']['Policy'])

        self.assertEqual(created_policy, expected_policy)
