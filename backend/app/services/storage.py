"""StorageService — vendor document uploads.

Design decisions and why
------------------------
*Uploads go through the backend, not straight from the browser.* A client
holding the anon key could otherwise write whatever it liked into the bucket.
Routing through here means every file is validated once, server-side, before it
exists anywhere.

*Type is decided by content, not by the client.* The declared Content-Type and
the filename extension are both attacker-controlled. A file is accepted only if
its leading bytes match a known signature AND the declared type agrees with what
those bytes say.

*The bucket is private.* Nothing is world-readable. A document is served through
a short-lived signed URL, minted only after the caller's right to see it has
been checked.

*The stored path is generated, never taken from input.* A caller-supplied
filename is the classic route to path traversal and to overwriting somebody
else's document. The object key is derived from the vendor id and a fresh UUID;
the original name is kept only as metadata for display.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from app.core.supabase_client import get_service_client

BUCKET = "vendor-documents"

MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB
MIN_FILE_BYTES = 64  # anything smaller cannot be a real document

# Declared type -> (extension, accepted leading-byte signatures)
ALLOWED_TYPES: dict[str, tuple[str, tuple[bytes, ...]]] = {
    "application/pdf": (".pdf", (b"%PDF-",)),
    "image/png": (".png", (b"\x89PNG\r\n\x1a\n",)),
    "image/jpeg": (".jpg", (b"\xff\xd8\xff",)),
}

SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]")


class UploadRejected(ValueError):
    """The file failed validation. The message is safe to show a user."""


@dataclass(frozen=True)
class StoredFile:
    path: str
    file_name: str
    mime_type: str
    size_bytes: int
    bucket: str = BUCKET

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


class StorageService:
    # ---------------- validation ----------------

    @staticmethod
    def validate(content: bytes, declared_type: str, original_name: str) -> tuple[str, str]:
        """Check size and content. Returns (mime_type, safe_display_name)."""
        size = len(content)
        if size < MIN_FILE_BYTES:
            raise UploadRejected("File is empty or too small to be a document.")
        if size > MAX_FILE_BYTES:
            raise UploadRejected(
                f"File is {size / 1_048_576:.1f} MB. The limit is "
                f"{MAX_FILE_BYTES // 1_048_576} MB."
            )

        declared = (declared_type or "").split(";")[0].strip().lower()
        if declared not in ALLOWED_TYPES:
            raise UploadRejected(
                f"Type {declared or 'unknown'} is not accepted. "
                f"Allowed: {', '.join(sorted(ALLOWED_TYPES))}."
            )

        # The bytes decide. A PDF renamed to .png, or a script sent as
        # application/pdf, fails here regardless of what the request claimed.
        _, signatures = ALLOWED_TYPES[declared]
        if not any(content.startswith(sig) for sig in signatures):
            raise UploadRejected(
                "File content does not match the declared type. "
                "Upload a genuine PDF, PNG or JPEG."
            )

        actual = next(
            (mime for mime, (_, sigs) in ALLOWED_TYPES.items() if any(content.startswith(s) for s in sigs)),
            None,
        )
        if actual != declared:
            raise UploadRejected("Declared type does not match the file content.")

        # The display name never becomes a path, but dot sequences are stripped
        # anyway so that nothing resembling traversal is stored or rendered.
        display = SAFE_NAME.sub("_", (original_name or "document").strip())
        display = re.sub(r"\.{2,}", ".", display).lstrip("._")[:120] or "document"
        return declared, display

    # ---------------- storage ----------------

    def _ensure_bucket(self) -> None:
        client = get_service_client()
        try:
            buckets = client.storage.list_buckets()
            names = {getattr(b, "name", None) or (b.get("name") if isinstance(b, dict) else None) for b in buckets}
            if BUCKET not in names:
                # Private: public=False. Never make this bucket public — the
                # documents are business licences and identity papers.
                client.storage.create_bucket(
                    BUCKET,
                    options={
                        "public": False,
                        "file_size_limit": MAX_FILE_BYTES,
                        "allowed_mime_types": sorted(ALLOWED_TYPES),
                    },
                )
        except Exception:  # noqa: BLE001 - creation races and existing buckets are fine
            pass

    def upload_vendor_document(
        self, vendor_id: str, content: bytes, declared_type: str, original_name: str
    ) -> StoredFile:
        mime, display = self.validate(content, declared_type, original_name)
        extension = ALLOWED_TYPES[mime][0]

        # Path is generated. Nothing from the client reaches it.
        path = f"vendors/{vendor_id}/{uuid.uuid4().hex}{extension}"

        self._ensure_bucket()
        client = get_service_client()
        client.storage.from_(BUCKET).upload(
            path,
            content,
            {"content-type": mime, "upsert": "false"},
        )

        return StoredFile(path=path, file_name=display, mime_type=mime, size_bytes=len(content))

    def signed_url(self, path: str, expires_in_seconds: int = 300) -> str:
        """Short-lived link to a private object.

        The caller must already have established that this person may see this
        document — this method does no authorization of its own.
        """
        client = get_service_client()
        result = client.storage.from_(BUCKET).create_signed_url(path, expires_in_seconds)
        if isinstance(result, dict):
            return result.get("signedURL") or result.get("signedUrl") or ""
        return str(result)

    def delete(self, path: str) -> None:
        get_service_client().storage.from_(BUCKET).remove([path])

    @staticmethod
    def describe() -> dict[str, Any]:
        return {
            "bucket": BUCKET,
            "public": False,
            "max_file_bytes": MAX_FILE_BYTES,
            "min_file_bytes": MIN_FILE_BYTES,
            "allowed_mime_types": sorted(ALLOWED_TYPES),
            "validation": "magic-byte signature must match the declared type",
            "path_policy": "server-generated: vendors/{vendor_id}/{uuid}.{ext}",
            "access": "short-lived signed URLs, issued after an authorization check",
        }


@lru_cache
def get_storage_service() -> StorageService:
    return StorageService()
