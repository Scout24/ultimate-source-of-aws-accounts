# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
import boto
import json

BUCKET_REGION = "eu-west-1"

class S3Uploader(object):

    def __init__(self, bucket_name, writer_arn, allowed_ips=None, allowed_aws_account_ids=None):
        self.bucket_name = bucket_name
        self.writer_arn = writer_arn
        self.allowed_ips = allowed_ips or []
        self.allowed_aws_account_ids = allowed_aws_account_ids or []
        self.conn = boto.s3.connect_to_region(BUCKET_REGION)

    def create_S3_bucket(self):
        """ Create a new S3 bucket if bucket not exists else nothing """
        try:
            self.conn.create_bucket(self.bucket_name)
        except boto.exception.S3CreateError:
            pass

    def set_S3_permissions(self):
        policy = {
            "Id": "Policy1445612972351",
            "Version": "2012-10-17",
            "Statement": [{
              "Sid": "Stmt1445612964522",
              "Action": [
                "s3:GetBucketLocation",
                "s3:GetBucketNotification",
                "s3:GetBucketRequestPayment",
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
            }]
        }

        bucket = self.conn.get_bucket(self.bucket_name)
        bucket.set_policy(json.dumps(policy))

    def setup_S3_webserver(self):
        pass

    def upload_to_S3(self, upload_data):
        bucket = self.conn.get_bucket(self.bucket_name)
        key = boto.s3.key.Key(bucket)

        for key_name, content in upload_data.items():
            key.key = key_name
            key.set_contents_from_string(content)
