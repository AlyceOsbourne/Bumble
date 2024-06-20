"""A bunch of codecs for converting the bytes post bumble.encode() to a different format"""
import base64
import bz2
import functools
import gzip
import hashlib
import lzma
import zlib
from enum import Enum

from bumble.utils.abstract_codec import Codec


def hash_encode(data: bytes, algo):
    """Encode the data with the given hash algorithm."""
    h = hashlib.new(algo)
    h.update(data)
    return h.digest() + data


def hash_decode(data: bytes, algo, length):
    """Decode the data with the given hash algorithm."""
    data_hash, data = data[:length], data[length:]
    h = hashlib.new(algo)
    h.update(data)
    if data_hash != h.digest():
        raise ValueError("Hash mismatch")
    return data


def binary_encode(data: bytes):
    """Encode the data as binary."""
    return ''.join(f'{byte:08b}' for byte in data).encode()


def binary_decode(data: bytes):
    """Decode the data from binary."""
    return bytes(int(data[i:i + 8], 2) for i in range(0, len(data), 8))


def null_encode(data: bytes):
    """Is just a pass through. Does nothing."""
    return data


def null_decode(data: bytes):
    """Is just a pass through. Does nothing."""
    return data


def rle_encode(data: bytes) -> bytes:
    """Run Length Encoding for the given data."""
    if not data:
        return b''

    char = 0x00  # Using 0x00 as the control character
    encoded = bytearray()
    prev_byte = data[0]
    count = 1

    for byte in data[1:]:
        if byte == prev_byte:
            count += 1
            if count == 256:
                encoded.extend([char, 255, prev_byte])
                count = 1
        else:
            if count > 1:
                encoded.extend([char, count, prev_byte])
            else:
                encoded.append(prev_byte)
            prev_byte = byte
            count = 1

    if count > 1:
        encoded.extend([char, count, prev_byte])
    else:
        encoded.append(prev_byte)

    return bytes(encoded)


def rle_decode(data: bytes) -> bytes:
    """Run Length Decoding for the given data."""
    if not data:
        return b''

    char = 0x00
    decoded = bytearray()
    it = iter(data)

    for byte in it:
        if byte == char:
            count = next(it)
            value = next(it)
            decoded.extend([value] * count)
        else:
            decoded.append(byte)

    return bytes(decoded)


class Codecs(Codec, Enum):
    """
    An enum of common codecs that can be used to encode and decode data.
    """
    AS_IS = NULL = (null_encode, null_decode)

    BIN = BINARY = (binary_encode, binary_decode)
    HEX = B16 = BASE16 = (base64.b16encode, base64.b16decode)
    B32 = BASE32 = (base64.b32encode, base64.b32decode)
    B64 = BASE64 = (base64.b64encode, base64.b64decode)
    B85 = BASE85 = (base64.b85encode, base64.b85decode)

    BZ2 = (bz2.compress, bz2.decompress)
    GZ = GZIP = (gzip.compress, gzip.decompress)
    ZLIB = (zlib.compress, zlib.decompress)
    LZMA = (lzma.compress, lzma.decompress)

    SHA1 = functools.partial(hash_encode, algo='sha1'), functools.partial(hash_decode, algo='sha1', length=20)
    SHA256 = functools.partial(hash_encode, algo='sha256'), functools.partial(hash_decode, algo='sha256', length=32)
    SHA512 = functools.partial(hash_encode, algo='sha512'), functools.partial(hash_decode, algo='sha512', length=64)
    MD5 = functools.partial(hash_encode, algo='md5'), functools.partial(hash_decode, algo='md5', length=16)

    RLE = (rle_encode, rle_decode)

    def __str__(self):
        return self.name


__all__ = ['Codecs']
