# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
import json
import logging

import boto3

BUCKET_REGION = "eu-west-1"


class S3Uploader(object):
    def __init__(self, bucket_name, allowed_ips=None, allowed_aws_account_ids=None):
        self.bucket_name = bucket_name
        self.allowed_ips = allowed_ips or []
        self.allowed_aws_account_ids = allowed_aws_account_ids or []
        self.boto3_s3_client = boto3.client('s3', region_name=BUCKET_REGION)
        self.boto3_sns_client = boto3.client('sns', region_name=BUCKET_REGION)

    def setup_infrastructure(self):
        topic_arn = self.create_sns_topic()
        self.set_sns_topic_policy(topic_arn)
        self.create_S3_bucket()
        self.set_S3_permissions()
        self.setup_S3_webserver()
        self.enable_bucket_notifications(topic_arn)

    def create_S3_bucket(self):
        """ Create a new S3 bucket if bucket not exists else nothing """
        try:
            self.boto3_s3_client.create_bucket(
                Bucket=self.bucket_name,
                CreateBucketConfiguration={'LocationConstraint': BUCKET_REGION})
            logging.debug("Created new AWS S3 bucket with name '%s'", self.bucket_name)
        except Exception as e:
            logging.debug("Could not create S3 bucket '%s': %s", self.bucket_name, e)

    def set_S3_permissions(self):
        policy = {
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
            }, {
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

        bucket_policy = boto3.resource('s3').BucketPolicy(self.bucket_name)
        bucket_policy.put(Policy=json.dumps(policy))
        logging.debug("AWS S3 bucket '%s' now has policy: '%s'", self.bucket_name, policy)

    def create_sns_topic(self):
        response = self.boto3_sns_client.create_topic(Name=self.bucket_name)
        topic_arn = response['TopicArn']
        logging.info("Using SNS topic with arn '%s'", topic_arn)

        return topic_arn

    def set_sns_topic_policy(self, topic_arn):
        allow_s3_events = {
            "Sid": "allow_s3_events",
            "Effect": "Allow",
            "Action": [
                "sns:Publish"
            ],
            "Principal": {
                "AWS": "*"
            },
            "Resource": topic_arn,
            "Condition": {
                "ArnLike": {
                    "aws:SourceArn": "arn:aws:s3:*:*:{0}".format(self.bucket_name)
                }
            }
        }
        allow_subscribe_to_all_acconts = {
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
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                allow_s3_events,
                allow_subscribe_to_all_acconts
            ]
        }

        self.boto3_sns_client.set_topic_attributes(
            TopicArn=topic_arn, AttributeName='Policy', AttributeValue=json.dumps(policy))

    def enable_bucket_notifications(self, topic_arn):
        notification_configuration = {
            'TopicConfigurations': [
                {
                    'TopicArn': topic_arn,
                    'Events': ['s3:ObjectCreated:*']
                }
            ]
        }
        self.boto3_s3_client.put_bucket_notification_configuration(
                Bucket=self.bucket_name,
                NotificationConfiguration=notification_configuration)

    def get_routing_rules(self):
        return [
            {
             'Condition': {'KeyPrefixEquals': 'yaml'},
             'Redirect': {'ReplaceKeyPrefixWith': 'accounts.yaml'}
            },
            {
             'Condition': {'KeyPrefixEquals': 'json'},
             'Redirect': {'ReplaceKeyPrefixWith': 'accounts.json'}
            }]

    def setup_S3_webserver(self):
        self.boto3_s3_client.put_bucket_website(
                Bucket=self.bucket_name,
                WebsiteConfiguration={
                    'IndexDocument': {'Suffix': 'accounts.json'},
                    'RoutingRules': self.get_routing_rules()
                })

    def upload_to_S3(self, upload_data):
        for key_name, content in upload_data.items():
            if key_name.endswith('json'):
                content_type = 'application/json'
            elif key_name.endswith('yaml'):
                content_type = 'application/yaml'
            else:
                content_type = 'application/text'
            self.boto3_s3_client.put_object(
                Bucket=self.bucket_name, Key=key_name,
                Body=content, ContentType=content_type)
            logging.debug("Uploaded to AWS S3 bucket '%s': "
                          "key '%s' and content '%s'", self.bucket_name, key_name, content)
