import base64
import binascii
import bz2
import functools
import gzip
import hashlib
import lzma
import zlib
from enum import Enum

from utils.abstract_codec import Codec


def hash_encode(data: bytes, algo):
    h = hashlib.new(algo)
    h.update(data)
    return h.digest() + data


def hash_decode(data: bytes, algo, length):
    data_hash, data = data[:length], data[length:]
    h = hashlib.new(algo)
    h.update(data)
    if data_hash != h.digest():
        raise ValueError("Hash mismatch")
    return data


class Codecs(Codec, Enum):
    AS_IS = NULL = (lambda data: data, lambda data: data)
    B64 = (base64.b64encode, base64.b64decode)
    HEX = (binascii.hexlify, binascii.unhexlify)
    BZ2 = (bz2.compress, bz2.decompress)
    GZ = (gzip.compress, gzip.decompress)
    ZLIB = (zlib.compress, zlib.decompress)
    LZMA = (lzma.compress, lzma.decompress)
    B32 = (base64.b32encode, base64.b32decode)
    B85 = (base64.b85encode, base64.b85decode)

    SHA256 = functools.partial(hash_encode, algo='sha256'), functools.partial(hash_decode, algo='sha256', length=32)
    SHA512 = functools.partial(hash_encode, algo='sha512'), functools.partial(hash_decode, algo='sha512', length=64)
    MD5 = functools.partial(hash_encode, algo='md5'), functools.partial(hash_decode, algo='md5', length=16)


__all__ = ['Codecs']