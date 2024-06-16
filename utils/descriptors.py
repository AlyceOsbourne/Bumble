import pickle
import pickletools
from typing import Protocol, Callable, runtime_checkable

from bumble import encode, decode
from utils.standard_codecs import Codec, Codecs


class Bumble:
    def __init__(self, codec: Codec = Codecs.NULL, replace_pickle: bool = True):
        self.codec = codec
        self.replace_pickle = replace_pickle

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.codec.encode(encode(instance.__dict__))

    def __set__(self, instance, value):
        instance.__dict__.update(decode(self.codec.decode(value)))

    def __set_name__(self, owner, name):
        if not self.replace_pickle:
            return

        def __getstate__(instance):
            return self.__get__(instance, owner)

        def __setstate__(instance, state):
            self.__set__(instance, state)

        owner.__getstate__ = __getstate__
        owner.__setstate__ = __setstate__


class Pickle:
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return pickletools.optimize(pickle.dumps(instance))

    def __set__(self, instance, value):
        instance.__dict__.update(pickle.loads(value).__dict__)


@runtime_checkable
class BumbleProtocol(Protocol):
    __bumble__: Bumble
    __pickle__: Pickle


def bumble(
        replace_pickle: bool = True  # you generally don't want to set this to False.
) -> Callable[[type], type[BumbleProtocol]]:
    def decorator(cls: type) -> type[BumbleProtocol]:
        codec = getattr(cls, '__codec__', Codecs.NULL)
        setattr(cls, '__bumble__', Bumble(codec, replace_pickle))
        setattr(cls, '__pickle__', Pickle())
        return cls  # type: ignore

    return decorator
