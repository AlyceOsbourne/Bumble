"""
.. include:: ../README.md
"""

from bumble_bencoding.codec import encode, decode  # noqa
from bumble_bencoding.utils.pipeline import Pipeline  # noqa

__version__ = "0.0.3"

__all__ = ['encode', 'decode', 'utils', 'codec']
