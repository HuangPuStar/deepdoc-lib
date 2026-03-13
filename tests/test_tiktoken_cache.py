import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


from deepdoc.common import tiktoken_cache as tc


class _FakeResponse:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def read(self) -> bytes:
        return self._data

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class TestTiktokenCache(unittest.TestCase):
    def setUp(self) -> None:
        self._old_env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._old_env)

    def test_resolve_tiktoken_cache_dir_uses_model_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            os.environ.pop("TIKTOKEN_CACHE_DIR", None)
            os.environ.pop(tc.DEEPDOC_TIKTOKEN_CACHE_DIR_ENV, None)
            os.environ["DEEPDOC_MODEL_HOME"] = tmp

            resolved = tc.resolve_tiktoken_cache_dir()

            self.assertEqual(resolved, Path(tmp).resolve().joinpath("tiktoken_cache"))

    def test_download_cl100k_base_writes_cache_key_named_file(self) -> None:
        payload = b"test-tiktoken-data"
        blob_url = "https://example.com/cl100k_base.tiktoken"
        expected_hash = hashlib.sha256(payload).hexdigest()

        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(tc, "urlopen", return_value=_FakeResponse(payload)) as mocked_urlopen:
                target = tc.download_cl100k_base(
                    cache_dir=tmp,
                    blob_url=blob_url,
                    expected_hash=expected_hash,
                )

            self.assertEqual(target, Path(tmp).resolve().joinpath(hashlib.sha1(blob_url.encode()).hexdigest()))
            self.assertEqual(target.read_bytes(), payload)
            mocked_urlopen.assert_called_once_with(blob_url, timeout=60)

    def test_download_cl100k_base_offline_uses_existing_cache(self) -> None:
        payload = b"cached-tiktoken-data"
        blob_url = "https://example.com/cl100k_base.tiktoken"
        expected_hash = hashlib.sha256(payload).hexdigest()

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp).resolve().joinpath(hashlib.sha1(blob_url.encode()).hexdigest())
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)

            with patch.object(tc, "urlopen") as mocked_urlopen:
                resolved = tc.download_cl100k_base(
                    cache_dir=tmp,
                    blob_url=blob_url,
                    expected_hash=expected_hash,
                    offline=True,
                )

            self.assertEqual(resolved, target)
            mocked_urlopen.assert_not_called()
