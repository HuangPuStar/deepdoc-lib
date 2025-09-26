import nltk
import logging
import threading
from functools import lru_cache, wraps
import ssl
import warnings

logger = logging.getLogger(__name__)

# Thread-safe download lock
_download_lock = threading.Lock()
_downloaded_resources: set[str] = set()


def _setup_ssl_context():
    """Setup SSL context for NLTK downloads."""
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context


@lru_cache(maxsize=None)
def ensure_nltk_resource(resource_path: str, download_name: str) -> bool:
    """
    Ensure NLTK resource is available, download automatically if needed.
    Thread-safe and cached.
    """
    # Fast path: check if already available
    try:
        nltk.data.find(resource_path)
        return True
    except LookupError:
        pass

    # Slow path: download if needed (thread-safe)
    with _download_lock:
        # Double-check pattern
        try:
            nltk.data.find(resource_path)
            return True
        except LookupError:
            pass

        # Avoid re-downloading if we already tried
        if download_name in _downloaded_resources:
            return False

        try:
            logger.info(f"Downloading NLTK resource: {download_name}")
            _setup_ssl_context()

            # Suppress NLTK download messages unless in debug mode
            with warnings.catch_warnings():
                if logger.getEffectiveLevel() > logging.DEBUG:
                    warnings.simplefilter("ignore")

                success = nltk.download(download_name, quiet=True)

            _downloaded_resources.add(download_name)

            if success:
                logger.debug(f"Successfully downloaded {download_name}")
                return True
            else:
                logger.warning(f"Failed to download {download_name}")
                return False

        except Exception as e:
            logger.error(f"Error downloading {download_name}: {e}")
            _downloaded_resources.add(download_name)  # Don't retry
            return False


def require_nltk_data(*resources):
    """
    Decorator that ensures NLTK resources are available.
    Works with functions, methods, and classes.

    Args:
        *resources: Tuples of (resource_path, download_name)
    """

    def decorator(target):
        # Handle class decoration
        if isinstance(target, type):
            # Decorate the class
            original_init = target.__init__

            @wraps(original_init)
            def new_init(self, *args, **kwargs):
                # Ensure resources before class initialization
                missing = []
                for resource_path, download_name in resources:
                    if not ensure_nltk_resource(resource_path, download_name):
                        missing.append(download_name)

                if missing:
                    raise RuntimeError(
                        f"Failed to download required NLTK resources: {', '.join(missing)}. "
                        f"Please check your internet connection or install manually: "
                        f"python -c \"import nltk; [nltk.download('{r}') for r in {missing}]\""
                    )

                return original_init(self, *args, **kwargs)

            target.__init__ = new_init
            return target

        # Handle function/method decoration
        else:

            @wraps(target)
            def wrapper(*args, **kwargs):
                missing = []
                for resource_path, download_name in resources:
                    if not ensure_nltk_resource(resource_path, download_name):
                        missing.append(download_name)

                if missing:
                    raise RuntimeError(
                        f"Failed to download required NLTK resources: {', '.join(missing)}. "
                        f"Please check your internet connection or install manually: "
                        f"python -c \"import nltk; [nltk.download('{r}') for r in {missing}]\""
                    )

                return target(*args, **kwargs)

            return wrapper

    return decorator
