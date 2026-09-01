import os
import uuid
import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")


def get_s3_client():
    """Initializes and returns the boto3 S3 client."""
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        return boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )
    return boto3.client("s3", region_name=AWS_REGION)


def is_s3_configured() -> bool:
    """Checks whether AWS S3 bucket name is configured in environment variables."""
    return bool(AWS_BUCKET_NAME)


def upload_image_to_s3(file_bytes: bytes, file_ext: str, content_type: str, folder: str = "avatars") -> str:
    """
    Uploads raw image bytes to AWS S3 and returns the public URL.
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
        return f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{unique_key}"
    except ClientError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image to AWS S3: {e.response['Error']['Message']}"
        )


def delete_image_from_s3(file_url: str) -> bool:
    """
    Deletes an image from S3 given its full URL if it belongs to our configured bucket.
    """
    if not is_s3_configured() or not file_url:
        return False

    client = get_s3_client()
    prefix = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/"

    if file_url.startswith(prefix):
        key = file_url[len(prefix):]
        try:
            client.delete_object(Bucket=AWS_BUCKET_NAME, Key=key)
            return True
        except ClientError:
            return False

    return False
