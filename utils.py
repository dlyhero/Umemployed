import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError

s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name='eu-north-1'
)

bucket_name = 'umemployed'
s3_key = 'resumes/ParthBhatt_Resume.pdf'

try:
    response = s3.head_object(Bucket=bucket_name, Key=s3_key)
    print("File exists:", response)
except ClientError as e:
    print("Error:", e)
except NoCredentialsError:
    print("Credentials not available")
