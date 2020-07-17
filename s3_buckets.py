import boto3
from botocore.exceptions import ClientError
import uuid


class S3Bucket:
    def __init__(self, bucket_name):
        """

        :param bucket_name:
        """
        self._bucket_name = f'{bucket_name}-{uuid.uuid4()}'

    def create_bucket(self):
        """

        :return:
        """
        s3client = boto3.client('s3')

        print(f'Creating new bucket: {self._bucket_name}')
        s3_response = s3client.create_bucket(Bucket=self._bucket_name)
        return {"S3Response" : s3_response}

    def upload_file_to_bucket(self):
        """[TO DO]"""
        pass