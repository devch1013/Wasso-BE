import os
import uuid
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from django.conf import settings


class S3Uploader:
    """
    AWS S3에 파일을 업로드하고 관리하는 유틸리티 클래스 (싱글톤 패턴)
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        self.file_server_url = settings.FILE_SERVER_URL
        self._initialized = True

    def get_file_url(self, file_path: str) -> str:
        return f"{self.file_server_url}{file_path}"

    def upload_file(self, file_field, directory: str = "") -> Optional[str]:
        """
        Django FileField로부터 파일을 S3에 업로드

        Args:
            file_field: Django FileField 객체
            directory: S3 버킷 내 저장될 디렉토리 경로 (선택사항)

        Returns:
            성공 시 S3 URL, 실패 시 None
        """
        try:
            file_name = f"{str(uuid.uuid4())}.jpg"
            file_path = os.path.join(directory, file_name) if directory else file_name

            self.s3_client.upload_fileobj(file_field.file, self.bucket_name, file_path)

            # S3 URL 생성
            return file_path

        except ClientError as e:
            print(f"Error uploading file to S3: {str(e)}")
            return None

    def delete_file(self, file_path: str) -> bool:
        """
        S3에서 파일 삭제

        Args:
            file_path: 삭제할 파일의 S3 경로

        Returns:
            성공 여부 (True/False)
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_path)
            return True

        except ClientError as e:
            print(f"Error deleting file from S3: {str(e)}")
            return False
