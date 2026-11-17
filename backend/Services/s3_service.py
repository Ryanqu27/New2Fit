import os
import uuid
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from fastapi import HTTPException

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_ENDPOINT_URL_S3 = os.getenv("AWS_ENDPOINT_URL_S3")


def get_s3_client():
    """Initializes and returns the boto3 S3 client with support for custom S3 endpoints (Neon, R2, AWS)."""
    kwargs = {
        "service_name": "s3",
        "region_name": AWS_REGION,
    }
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        kwargs["aws_access_key_id"] = AWS_ACCESS_KEY_ID
        kwargs["aws_secret_access_key"] = AWS_SECRET_ACCESS_KEY

    if AWS_ENDPOINT_URL_S3:
        kwargs["endpoint_url"] = AWS_ENDPOINT_URL_S3
        # Neon and many S3-compatible providers require path-style addressing
        kwargs["config"] = Config(s3={"addressing_style": "path"})

    return boto3.client(**kwargs)


def is_s3_configured() -> bool:
    """Checks whether AWS S3 bucket name is configured in environment variables."""
    return bool(AWS_BUCKET_NAME)


def upload_image_to_s3(file_bytes: bytes, file_ext: str, content_type: str, folder: str = "avatars") -> str:
    """
    Uploads raw image bytes to S3-compatible object storage and returns the public URL.
    """
    if not is_s3_configured():
        raise ValueError("AWS_BUCKET_NAME environment variable is not configured.")

    client = get_s3_client()
    clean_ext = file_ext.lstrip(".")
    unique_key = f"{folder}/{uuid.uuid4()}.{clean_ext}"

    try:
        client.put_object(
            Bucket=AWS_BUCKET_NAME,
            Key=unique_key,
            Body=file_bytes,
            ContentType=content_type,
        )
        if AWS_ENDPOINT_URL_S3:
            return f"{AWS_ENDPOINT_URL_S3.rstrip('/')}/{AWS_BUCKET_NAME}/{unique_key}"
        return f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{unique_key}"
    except ClientError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image to S3: {e.response['Error']['Message']}"
        )


def delete_image_from_s3(file_url: str) -> bool:
    """
    Deletes an image from S3 given its full URL if it belongs to our configured bucket.
    """
    if not is_s3_configured() or not file_url:
        return False

    client = get_s3_client()

    key = None
    # Check Neon / custom endpoint prefix
    if AWS_ENDPOINT_URL_S3:
        custom_prefix = f"{AWS_ENDPOINT_URL_S3.rstrip('/')}/{AWS_BUCKET_NAME}/"
        if file_url.startswith(custom_prefix):
            key = file_url[len(custom_prefix):]

    # Check standard AWS prefix
    aws_prefix = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/"
    if not key and file_url.startswith(aws_prefix):
        key = file_url[len(aws_prefix):]

    if key:
        try:
            client.delete_object(Bucket=AWS_BUCKET_NAME, Key=key)
            return True
        except ClientError:
            return False

    return False
