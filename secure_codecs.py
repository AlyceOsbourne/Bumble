import base64
import hashlib
from typing import AnyStr

from cryptography.fernet import Fernet

from standard_codecs import Codec

import hmac

def EncryptedCodec(key: AnyStr) -> Codec:
    if isinstance(key, str):
        key = key.encode()
    key = base64.urlsafe_b64encode(hashlib.sha256(key).digest())
    cipher = Fernet(key)
    return Codec(
        encode=cipher.encrypt,
        decode=cipher.decrypt
    )

def HMACCodec(key: AnyStr) -> Codec:
    if isinstance(key, str):
        key = key.encode()
    return Codec(
        encode=lambda data: hmac.new(key, data, hashlib.sha256).digest() + data,
        decode=lambda data: data[32:] if hmac.compare_digest(data[:32], hmac.new(key, data[32:], hashlib.sha256).digest()) else None
    )


class SecureCodec:
    def __init__(self, codec: type[Codec]):
        self.codec = codec

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.codec(instance.key)

    def __set__(self, instance, value):
        instance.key = value