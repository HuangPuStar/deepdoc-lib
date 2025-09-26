import os
import logging

LIGHTEN = int(os.environ.get("DEEPDOC_LIGHTEN", "0"))

PARALLEL_DEVICES = 0
try:
    import torch.cuda
    PARALLEL_DEVICES = torch.cuda.device_count()
    logging.info(f"Found {PARALLEL_DEVICES} GPUs")
except Exception as e:
    logging.info("Can't import package 'torch' or access GPU: %s", str(e))