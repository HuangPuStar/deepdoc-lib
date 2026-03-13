from __future__ import annotations

import hashlib
import os
import uuid
from pathlib import Path
from urllib.request import urlopen


DEEPDOC_TIKTOKEN_CACHE_DIR_ENV = "DEEPDOC_TIKTOKEN_CACHE_DIR"
CL100K_BASE_BLOB_URL = "https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken"
CL100K_BASE_EXPECTED_HASH = "223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7"


def resolve_tiktoken_cache_dir(cache_dir: str | None = None, model_home: str | None = None) -> Path:
    if cache_dir:
        return Path(cache_dir).expanduser().resolve()

    explicit_cache_dir = os.getenv(DEEPDOC_TIKTOKEN_CACHE_DIR_ENV) or os.getenv("TIKTOKEN_CACHE_DIR")
    if explicit_cache_dir:
        return Path(explicit_cache_dir).expanduser().resolve()

    configured_model_home = model_home or os.getenv("DEEPDOC_MODEL_HOME")
    if configured_model_home:
        return Path(configured_model_home).expanduser().resolve().joinpath("tiktoken_cache")

    return Path.home().joinpath(".cache", "deepdoc", "tiktoken_cache").resolve()


def configure_tiktoken_cache_env(cache_dir: str | None = None, model_home: str | None = None) -> str:
    resolved_cache_dir = resolve_tiktoken_cache_dir(cache_dir=cache_dir, model_home=model_home)
    os.environ["TIKTOKEN_CACHE_DIR"] = str(resolved_cache_dir)
    return str(resolved_cache_dir)


def cl100k_base_cache_key(blob_url: str = CL100K_BASE_BLOB_URL) -> str:
    return hashlib.sha1(blob_url.encode()).hexdigest()


def _matches_expected_hash(data: bytes, expected_hash: str | None) -> bool:
    if not expected_hash:
        return True
    return hashlib.sha256(data).hexdigest() == expected_hash


def download_cl100k_base(
    *,
    cache_dir: str | None = None,
    model_home: str | None = None,
    offline: bool = False,
    blob_url: str = CL100K_BASE_BLOB_URL,
    expected_hash: str = CL100K_BASE_EXPECTED_HASH,
    timeout: int = 60,
) -> Path:
    resolved_cache_dir = resolve_tiktoken_cache_dir(cache_dir=cache_dir, model_home=model_home)
    cache_key = cl100k_base_cache_key(blob_url)
    target_path = resolved_cache_dir.joinpath(cache_key)

    if target_path.exists():
        data = target_path.read_bytes()
        if _matches_expected_hash(data, expected_hash):
            return target_path
        target_path.unlink()

    if offline:
        raise FileNotFoundError(
            "Missing cached tiktoken encoder '{}'. Expected file at {}. Run the download command without --offline first."
            .format(cache_key, target_path)
        )

    with urlopen(blob_url, timeout=timeout) as response:
        data = response.read()

    if not _matches_expected_hash(data, expected_hash):
        raise ValueError(
            "Hash mismatch for tiktoken encoder downloaded from {}. Expected SHA256 {}."
            .format(blob_url, expected_hash)
        )

    resolved_cache_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = target_path.with_name("{}.{}.tmp".format(target_path.name, uuid.uuid4().hex))
    tmp_path.write_bytes(data)
    tmp_path.replace(target_path)
    return target_path
