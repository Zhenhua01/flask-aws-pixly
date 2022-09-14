import os
import boto3

# s3 = boto3.resource('s3')

s3 = boto3.client(
  "s3",
  "us-west-1",
  aws_access_key_id = os.environ['ACCESS_KEY_ID'],
  aws_secret_access_key = os.environ['SECRET_ACCESS_KEY']
)
bucket_name = os.environ['BUCKET_NAME']

def get_images():
    for bucket in s3.buckets.all():
        print(bucket.name)

def upload_images():
    print("upload")


