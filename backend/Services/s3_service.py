import os
import uuid
import logging
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from fastapi import HTTPException

logger = logging.getLogger(__name__)


def _clean_env(key: str, default: str = None) -> str:
    """Gets an environment variable and strips surrounding quotes, spaces, and newlines."""
    val = os.getenv(key, default)
    if val:
        val = val.strip().strip('"').strip("'").strip()
    return val or None


def get_s3_config():
    """Returns cleaned S3 configuration from environment variables."""
    return {
        "access_key_id": _clean_env("AWS_ACCESS_KEY_ID"),
        "secret_access_key": _clean_env("AWS_SECRET_ACCESS_KEY"),
        "region": _clean_env("AWS_REGION", "us-east-1"),
        "bucket_name": _clean_env("AWS_BUCKET_NAME", "new2fit-avatars"),
        "endpoint_url": _clean_env("AWS_ENDPOINT_URL_S3"),
    }


def get_s3_client():
    """Initializes and returns the boto3 S3 client with support for custom S3 endpoints (Neon, R2, AWS)."""
    cfg = get_s3_config()
    kwargs = {
        "service_name": "s3",
        "region_name": cfg["region"],
    }
    if cfg["access_key_id"] and cfg["secret_access_key"]:
        kwargs["aws_access_key_id"] = cfg["access_key_id"]
        kwargs["aws_secret_access_key"] = cfg["secret_access_key"]

    if cfg["endpoint_url"]:
        kwargs["endpoint_url"] = cfg["endpoint_url"]
        # Neon and many S3-compatible providers require path-style addressing
        kwargs["config"] = Config(s3={"addressing_style": "path"})

    return boto3.client(**kwargs)


def is_s3_configured() -> bool:
    """Checks whether S3 bucket name is configured in environment variables."""
    cfg = get_s3_config()
    return bool(cfg["bucket_name"])


def upload_image_to_s3(file_bytes: bytes, file_ext: str, content_type: str, folder: str = "avatars") -> str:
    """
    Uploads raw image bytes to S3-compatible object storage and returns the public URL.
    """
    cfg = get_s3_config()
    bucket_name = cfg["bucket_name"]
    endpoint_url = cfg["endpoint_url"]
    region = cfg["region"]
    key_prefix = (cfg["access_key_id"][:12] + "...") if cfg["access_key_id"] else "None"

    if not is_s3_configured():
        raise ValueError("AWS_BUCKET_NAME environment variable is not configured.")

    debug_msg = f"[S3 UPLOAD] endpoint={endpoint_url or '(DEFAULT AWS S3)'} | bucket={bucket_name} | key_id={key_prefix} | region={region}"
    print(debug_msg, flush=True)

    client = get_s3_client()
    clean_ext = file_ext.lstrip(".")
    unique_key = f"{folder}/{uuid.uuid4()}.{clean_ext}"

    try:
        client.put_object(
            Bucket=bucket_name,
            Key=unique_key,
            Body=file_bytes,
            ContentType=content_type,
        )
        if endpoint_url:
            return f"{endpoint_url.rstrip('/')}/{bucket_name}/{unique_key}"
        return f"https://{bucket_name}.s3.{region}.amazonaws.com/{unique_key}"
    except Exception as e:
        logger.exception("Failed to upload image to S3: %s", e)
        error_msg = e.response["Error"]["Message"] if isinstance(e, ClientError) and "Error" in getattr(e, "response", {}) else str(e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image to S3 [endpoint={endpoint_url or 'DEFAULT_AWS_S3'}, key={key_prefix}]: {error_msg}"
        )


def delete_image_from_s3(file_url: str) -> bool:
    """
    Deletes an image from S3 given its full URL if it belongs to our configured bucket.
    """
    if not is_s3_configured() or not file_url:
        return False

    cfg = get_s3_config()
    bucket_name = cfg["bucket_name"]
    endpoint_url = cfg["endpoint_url"]
    region = cfg["region"]

    client = get_s3_client()

    key = None
    # Check Neon / custom endpoint prefix
    if endpoint_url:
        custom_prefix = f"{endpoint_url.rstrip('/')}/{bucket_name}/"
        if file_url.startswith(custom_prefix):
            key = file_url[len(custom_prefix):]

    # Check standard AWS prefix
    aws_prefix = f"https://{bucket_name}.s3.{region}.amazonaws.com/"
    if not key and file_url.startswith(aws_prefix):
        key = file_url[len(aws_prefix):]

    if key:
        try:
            client.delete_object(Bucket=bucket_name, Key=key)
            return True
        except Exception as e:
            logger.warning("Could not delete old image from S3: %s", e)
            return False

    return False
