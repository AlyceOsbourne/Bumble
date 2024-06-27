"""Pipelines allow you to chain Bumbles codec with others with ease, allowing for you to create serialization
pipelines."""
import dataclasses

import bumble_bencoding
from .abstract_codec import Codec
from .standard_codecs import Codecs
import functools
import operator


@dataclasses.dataclass
class Pipeline:
    """
    The Pipeline class is used to create a serialization pipeline with Bumbles codec and other codecs.
    It accepts a codec and behaves just like codecs, but encodes/decodes to the bumble encoding first.

    Attributes:
        codec (Codec): The codec used in the pipeline. Default is Codecs.NULL.
    """

    codec: Codec = Codecs.NULL

    def encode[T](self, data: T, optimize=True) -> bytes:
        """
        Encodes the given object to Bumble bytes using the codec.

        Parameters:
           data (T): The data to be encoded.

        Returns:
           bytes: The encoded data.
        """
        return self.codec.encode(bumble_bencoding.encode(data, optimize=optimize))

    def decode[T](self, data: bytes) -> T:
        """
        Decodes objects from the given Bumble bytes using the codec.

        Parameters:
           data (bytes): The data to be decoded.

        Returns:
           T: The decoded data.
        """
        return bumble_bencoding.decode(self.codec.decode(data))

    @classmethod
    def of(cls, *item) -> 'Pipeline':
        """
        Creates a new Pipeline instance with the given codecs.

        Parameters:
           *item (str or Codec): The codecs to be used in the pipeline.

        Returns:
           Pipeline: A new Pipeline instance.
        """
        return cls(functools.reduce(operator.or_, [
            bumble_bencoding.utils.standard_codecs.Codecs[codec.upper()] if isinstance(codec, str) else codec
            for codec
            in item
        ])) if item else cls()

    def __or__[P:'Pipeline', C: 'Codec'](self, other: P | C | str) -> 'Pipeline':
        """
        Creates a new Pipeline instance with the given codecs.
        """
        if isinstance(other, Pipeline):
            other = other.codec
        elif isinstance(other, str):
            other = bumble_bencoding.utils.standard_codecs.Codecs[other.upper()]
        return Pipeline(self.codec | other)

    def __repr__(self) -> str:
        return f"Pipeline({self.codec})"


__all__ = ['Pipeline']
