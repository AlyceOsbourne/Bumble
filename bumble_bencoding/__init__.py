"""
.. include:: ../README.md
"""

from bumble_bencoding.codec import encode, decode  # noqa
from bumble_bencoding.utils.pipeline import Pipeline  # noqa

optimized_encode = Pipeline.of('LZMA', 'GZIP', 'BZ2')  # noqa
optimized_decode = Pipeline.of('LZMA', 'GZIP', 'BZ2')  # noqa


__version__ = "0.0.3"

__all__ = ['encode', 'decode', 'utils', 'codec']
