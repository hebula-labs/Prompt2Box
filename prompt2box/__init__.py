"""Prompt2Box — Gemini object detection in one import.

    from prompt2box import detect

    result = detect("photo.jpg")          # uses GEMINI_API_KEY
    print(result.labels)                  # ['cat', 'sofa', 'lamp']
    result.save_annotated("out.jpg")      # boxes drawn on a copy

For repeated calls, build a Detector once:

    from prompt2box import Detector
    det = Detector(model="gemini-2.5-flash")
    boxes = det.detect("photo.jpg", classes=["cat", "dog"])
    results = det.detect_batch(["a.jpg", "b.jpg"])   # concurrent
"""

import logging
from importlib.metadata import PackageNotFoundError, version

from prompt2box.detector import (
    DEFAULT_MODEL,
    Detection,
    DetectionResult,
    Detector,
    detect,
)
from prompt2box.refine import RefineConfig

try:
    __version__ = version("prompt2box")
except PackageNotFoundError:  # running from a source tree without install
    __version__ = "0.0.0+dev"

# Library convention: attach a NullHandler so applications that never configure
# logging see no "No handlers could be found" noise, while applications that do
# configure it still receive our records.
logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = [
    "detect",
    "Detector",
    "Detection",
    "DetectionResult",
    "RefineConfig",
    "DEFAULT_MODEL",
    "__version__",
]
