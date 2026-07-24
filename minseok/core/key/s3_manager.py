"""S3 클라이언트 — IAM 액세스 키는 `secret_manager`가 관리한다(코드에 키 금지).

실행(버킷 목록 출력): `minseok/`에서 `python -m core.key.s3_manager`
"""

from __future__ import annotations

import boto3

from core.key.secret_manager import get_secret_manager


def s3_client():
    """.env의 `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_DEFAULT_REGION`으로 클라이언트를 만든다."""
    secrets = get_secret_manager()
    return boto3.client(
        "s3",
        aws_access_key_id=secrets.require("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=secrets.require("AWS_SECRET_ACCESS_KEY"),
        region_name=secrets.get("AWS_DEFAULT_REGION", "ap-northeast-2"),
    )


def list_buckets() -> list[str]:
    """계정의 버킷 이름 목록."""
    return [bucket["Name"] for bucket in s3_client().list_buckets()["Buckets"]]


if __name__ == "__main__":
    for name in list_buckets():
        print(name)
