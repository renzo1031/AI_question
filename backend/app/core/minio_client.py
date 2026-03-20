"""
MinIO 对象存储客户端封装

通过 asyncio.run_in_executor 将同步 minio SDK 包装为异步接口。
"""
import asyncio
import io
import uuid
from functools import partial

from minio import Minio
from minio.error import S3Error

from app.core.config import settings


class MinioClient:
    def __init__(self) -> None:
        self._client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self._bucket = settings.minio_bucket
        self._public_url = settings.minio_public_url.rstrip("/")

    def _run(self, func, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(None, partial(func, *args, **kwargs))

    async def ensure_bucket(self) -> None:
        def _ensure():
            if not self._client.bucket_exists(self._bucket):
                self._client.make_bucket(self._bucket)

        await self._run(_ensure)

    async def upload_file(
        self,
        data: bytes,
        content_type: str,
        object_key: str | None = None,
    ) -> tuple[str, str]:
        """上传文件到 MinIO，返回 (object_key, public_url)"""
        if object_key is None:
            ext = content_type.split("/")[-1] if "/" in content_type else "bin"
            object_key = f"banners/{uuid.uuid4().hex}.{ext}"

        await self.ensure_bucket()

        def _upload():
            self._client.put_object(
                bucket_name=self._bucket,
                object_name=object_key,
                data=io.BytesIO(data),
                length=len(data),
                content_type=content_type,
            )

        await self._run(_upload)
        public_url = f"{self._public_url}/{self._bucket}/{object_key}"
        return object_key, public_url

    async def delete_file(self, object_key: str) -> None:
        """从 MinIO 删除文件（对象不存在时静默忽略）"""

        def _delete():
            try:
                self._client.remove_object(self._bucket, object_key)
            except S3Error:
                pass

        await self._run(_delete)


minio_client = MinioClient()
