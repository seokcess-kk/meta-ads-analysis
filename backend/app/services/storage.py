import logging
import uuid
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)


class S3Storage:
    """S3 storage service for ad images."""

    def __init__(self):
        self.bucket_name = settings.s3_bucket_name
        self.region = settings.aws_region
        self._client = None

    @property
    def client(self):
        """Get or create S3 client."""
        if self._client is None:
            self._client = boto3.client(
                "s3",
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=self.region,
            )
        return self._client

    def upload_image(
        self,
        image_data: bytes,
        ad_id: str,
        content_type: str = "image/png",
    ) -> Optional[str]:
        """
        Upload image to S3.

        Args:
            image_data: Image bytes
            ad_id: Ad ID for naming
            content_type: MIME type of the image

        Returns:
            S3 path (key) or None if failed
        """
        try:
            # Generate unique filename
            extension = content_type.split("/")[-1] if "/" in content_type else "png"
            filename = f"ads/{ad_id}/{uuid.uuid4().hex}.{extension}"

            self.client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=image_data,
                ContentType=content_type,
            )

            logger.info(f"Uploaded image to S3: {filename}")
            return filename

        except ClientError as e:
            logger.error(f"Error uploading to S3: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading to S3: {e}")
            return None

    def get_image_url(self, s3_path: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate pre-signed URL for image.

        Args:
            s3_path: S3 key/path
            expiration: URL expiration time in seconds

        Returns:
            Pre-signed URL or None if failed
        """
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_path},
                ExpiresIn=expiration,
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating pre-signed URL: {e}")
            return None

    def delete_image(self, s3_path: str) -> bool:
        """
        Delete image from S3.

        Args:
            s3_path: S3 key/path

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=s3_path)
            logger.info(f"Deleted image from S3: {s3_path}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting from S3: {e}")
            return False

    def check_bucket_exists(self) -> bool:
        """Check if the configured bucket exists."""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError:
            return False


# Singleton instance
storage = S3Storage()
