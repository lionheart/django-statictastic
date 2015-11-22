import random
import boto
from time import time

from django.core.management.base import BaseCommand
from django.conf import settings

email_sending_policy = """{{
  "Statement": [
    {{
      "Sid": "Stmt{0}",
      "Action": [
        "ses:GetSendQuota",
        "ses:GetSendStatistics",
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Effect": "Allow",
      "Resource": [
        "*"
      ]
    }}
  ]
}}"""

cloudfront_invalidation_policy = """{{
  "Statement": [
    {{
      "Sid": "Stmt{0}",
      "Action": [
        "cloudfront:CreateInvalidation"
      ],
      "Effect": "Allow",
      "Resource": [
        "*"
      ]
    }}
  ]
}}"""

generic_upload_policy = """{{
  "Statement": [
    {{
      "Sid": "Stmt{0}",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:ListBucket",
        "s3:PutBucketAcl"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::{1}",
        "arn:aws:s3:::{1}/*",
        "arn:aws:s3:::{2}",
        "arn:aws:s3:::{2}/*"
      ]
    }}
  ]
}}"""

upload_policy = """{{
  "Statement": [
    {{
      "Sid": "Stmt{0}",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:ListBucket"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::{1}",
        "arn:aws:s3:::{1}/*"
      ]
    }}
  ]
}}"""

static_upload_policy = """{{
  "Statement": [
    {{
      "Sid": "Stmt{0}",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:ListBucket"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::{1}",
        "arn:aws:s3:::{1}/*"
      ]
    }}
  ]
}}"""

from boto.s3.connection import OrdinaryCallingFormat

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        KEY = input("Enter the AWS Access Key ID: ")
        SECRET = input("Enter the AWS Secret Access Key: ")
        PROJECT_NAME = input("Enter the project name (e.g., aurora): ")

        iam_conn = boto.connect_iam(KEY, SECRET)
        s3_conn = boto.connect_s3(KEY, SECRET, calling_format=OrdinaryCallingFormat())
        cf_conn = boto.connect_cloudfront(KEY, SECRET)
        setting_parameters = []

        def create_group(group="Bots", path="/bots/"):
            print("Creating {} group...".format(group), end=' ')
            try:
                group = iam_conn.get_group(group)
            except boto.exception.BotoServerError as e:
                if e.error_code == "NoSuchEntity":
                    group = iam_conn.create_group(group, path=path)
                    print("success!")
            else:
                print("already exists, skipping.")

        def create_user(username, group="Bots", path="/bots/", policies={}):
            print("Creating {} user...".format(username), end=' ')
            try:
                user = iam_conn.get_user(username)
            except boto.exception.BotoServerError as e:
                if e.error_code == "NoSuchEntity":
                    user = iam_conn.create_user(username, path=path)
                    response = iam_conn.create_access_key(username)
                    print("success!")

                    access_key_id = response.create_access_key_response \
                            .create_access_key_result.access_key.access_key_id
                    secret_access_key = response.create_access_key_response \
                            .create_access_key_result.access_key.secret_access_key

                    print("AWS_ACCESS_KEY_ID = '{}'".format(access_key_id))
                    print("AWS_SECRET_ACCESS_KEY = '{}'".format(secret_access_key))

                    for name, policy in policies.items():
                        iam_conn.put_user_policy(username, name, policy)
                        print("\tAttaching {}".format(name))

                    iam_conn.add_user_to_group(group, username)
                    print("\tAdding to {}".format(group))
            else:
                print("already exists, skipping.")

        def create_cloudfront_distribution(bucket_name, cname):
            origin = boto.cloudfront.origin.S3Origin( \
                    "{}.s3.amazonaws.com".format(bucket_name))
            try:
                print("Creating CloudFront distribution for {}...".format(bucket_name), end=' ')
                distribution = cf_conn.create_distribution(origin, True,
                        cnames=[cname])
                print("success!")
                print("\tDistribution ID: {}".format(distribution.id))
                print("\tDomain name: {}".format(distribution.domain_name))
            except boto.cloudfront.CloudFrontServerError as e:
                if e.error_code == "CNAMEAlreadyExists":
                    print("already exists, skipping.")

        # Create buckets
        upload_bucket_name = "uploads-{}".format(PROJECT_NAME)
        static_bucket_name = "static-{}".format(PROJECT_NAME)

        upload_cname = "u-{}".format(PROJECT_NAME)
        static_cname = "s-{}".format(PROJECT_NAME)

        s3_conn.create_bucket(upload_bucket_name)
        s3_conn.create_bucket(static_bucket_name)

        print("AWS_STATIC_STORAGE_BUCKET_NAME = '{}'".format(static_bucket_name))
        print("AWS_STORAGE_BUCKET_NAME = '{}'".format(upload_bucket_name))

        # Create CloudFront Distribution
        create_cloudfront_distribution(upload_bucket_name, upload_cname)
        create_cloudfront_distribution(static_bucket_name, static_cname)

        # Create IAM Users
        unix_time = str(int(time()))

        create_group("Bots")
        create_user("{}FileUploader".format(PROJECT_NAME.capitalize()), policies={
            'GenericUploadPolicy': generic_upload_policy.format(unix_time, static_bucket_name, upload_bucket_name),
            'CloudFrontInvalidationPolicy': cloudfront_invalidation_policy.format(unix_time) })
        create_user("{}EmailSender".format(PROJECT_NAME.capitalize()), policies={
            'EmailSendingPolicy': email_sending_policy.format(unix_time) })


