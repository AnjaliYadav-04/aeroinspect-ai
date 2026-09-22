import os
import boto3
from typing import Optional
from botocore.exceptions import ClientError
from config import settings

class StorageService:
    def __init__(self):
        self.use_s3 = bool(settings.AWS_ACCESS_KEY_ID and settings.S3_BUCKET)
        if self.use_s3:
            self.s3 = boto3.client("s3", aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, region_name=settings.AWS_REGION)
            self.bucket = settings.S3_BUCKET

    async def upload_file(self, file_path: str, key: str) -> Optional[str]:
        if not self.use_s3: return None
        try:
            self.s3.upload_file(file_path, self.bucket, key)
            return f"https://{self.bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
        except ClientError as e:
            print(f"S3 upload error: {e}")
            return None

    async def get_presigned_url(self, key: str, expiration: int = 3600) -> Optional[str]:
        if not self.use_s3: return None
        try:
            return self.s3.generate_presigned_url("get_object", Params={"Bucket": self.bucket, "Key": key}, ExpiresIn=expiration)
        except ClientError as e:
            print(f"S3 URL error: {e}")
            return None

storage_service = StorageService()
