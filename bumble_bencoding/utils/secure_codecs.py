"""Codecs for encryption and secure hashing in the Bumble Library"""

import base64
import hashlib
import hmac
from typing import AnyStr

from cryptography.fernet import Fernet

from bumble_bencoding.utils.abstract_codec import Codec


def fernet_codec(key: AnyStr) -> Codec:
    """Create a Fernet codec with the given key. The key is hashed using SHA256 before being used."""
    if isinstance(key, str):
        key = key.encode()
    key = base64.urlsafe_b64encode(hashlib.sha256(key).digest())
    cipher = Fernet(key)
    return Codec(
        encode=cipher.encrypt,
        decode=cipher.decrypt
    )


def hmac_codec(key: AnyStr) -> Codec:
    """Create a HMAC codec with the given key."""
    if isinstance(key, str):
        key = key.encode()

    def encode(data: bytes) -> bytes:
        """Encode the data with the given key."""
        return hmac.new(key, data, hashlib.sha256).digest() + data

    def decode(data: bytes) -> bytes:
        """Decode the data with the given key."""
        return data[32:] if hmac.compare_digest(data[:32], hmac.new(key, data[32:], hashlib.sha256).digest()) else None

    return Codec(encode, decode)


__all__ = ['fernet_codec', 'hmac_codec']
