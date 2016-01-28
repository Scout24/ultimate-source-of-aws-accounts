# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
import boto.s3
import boto.exception
import boto.sns
import json
import logging

import boto3

BUCKET_REGION = "eu-west-1"


class S3Uploader(object):
    def __init__(self, bucket_name, allowed_ips=None, allowed_aws_account_ids=None):
        self.bucket_name = bucket_name
        self.allowed_ips = allowed_ips or []
        self.allowed_aws_account_ids = allowed_aws_account_ids or []
        self.s3_conn = boto.s3.connect_to_region(BUCKET_REGION)
        self.boto3_s3_client = boto3.client('s3')
        self.sns_conn = boto.sns.connect_to_region(BUCKET_REGION)

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
            self.s3_conn.create_bucket(self.bucket_name, location=BUCKET_REGION)
            logging.debug("Created new AWS S3 bucket with name '%s'", self.bucket_name)
        except boto.exception.S3CreateError as e:
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

        bucket = self.s3_conn.get_bucket(self.bucket_name)
        bucket.set_policy(json.dumps(policy))
        logging.debug("AWS S3 bucket '%s' now has policy: '%s'", self.bucket_name, policy)

    def create_sns_topic(self):
        response = self.sns_conn.create_topic(self.bucket_name)
        topic_arn = response['CreateTopicResponse']['CreateTopicResult']['TopicArn']
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

        dumps = json.dumps(policy)
        print(dumps)
        self.sns_conn.set_topic_attributes(topic_arn, 'Policy', dumps)

    def enable_bucket_notifications(self, topic_arn):
        notification_configuration = {
            'TopicConfigurations': [
                {
                    'TopicArn': topic_arn,
                    'Events': ['s3:ObjectCreated:*']
                }
            ]
        }
        self.boto3_s3_client.put_bucket_notification_configuration(Bucket=self.bucket_name,
                                                                   NotificationConfiguration=notification_configuration)

    def get_routing_rules(self):
        routing_rules = boto.s3.website.RoutingRules()
        for suffix in ['json', 'yaml']:
            condition = boto.s3.website.Condition(key_prefix=suffix)
            redirect = boto.s3.website.Redirect(replace_key_prefix='accounts.{0}'.format(suffix))
            routing_rules.add_rule(boto.s3.website.RoutingRule(condition, redirect))
        return routing_rules

    def setup_S3_webserver(self):
        bucket = self.s3_conn.get_bucket(self.bucket_name)

        index_key = bucket.new_key('accounts.json')
        index_key.content_type = 'application/json'

        # now set the website configuration for our bucket
        bucket.configure_website(suffix='accounts.json', routing_rules=self.get_routing_rules())
        logging.debug("Website configuration was setup for AWS S3 bucket '%s'", self.bucket_name)

    def upload_to_S3(self, upload_data):
        bucket = self.s3_conn.get_bucket(self.bucket_name)
        key = boto.s3.key.Key(bucket)

        for key_name, content in upload_data.items():
            key.key = key_name
            key.set_contents_from_string(content)
            logging.debug("Uploaded to AWS S3 bucket '%s': "
                          "key '%s' and content '%s'", self.bucket_name, key_name, content)
