"""Pipelines allow you to chain Bumbles codec with others with ease, allowing for you to create serialization pipelines."""

import bumble
from .abstract_codec import Codec
from .standard_codecs import Codecs
import functools
import operator

class Pipeline:
    """
    The Pipeline class is used to create a serialization pipeline with Bumble's codec and other codecs.
    It accepts a codec and behaves just like codecs, but encodes/decodes to the bumble encoding first.

    Attributes:
        codec (Codec): The codec used in the pipeline. Default is Codecs.NULL.
    """

    def __init__(self, codec: Codec = Codecs.NULL):
        """
        The constructor for Pipeline class.

        Parameters:
           codec (Codec): The codec used in the pipeline. Default is Codecs.NULL.
        """
        self.codec = codec

    def encode[T](self, data: T) -> bytes:
        """
        Encodes the given object to Bumble bytes using the codec.

        Parameters:
           data (T): The data to be encoded.

        Returns:
           bytes: The encoded data.
        """
        return self.codec.encode(bumble.encode(data))

    def decode[T](self, data: bytes) -> T:
        """
        Decodes objects from the given Bumble bytes using the codec.

        Parameters:
           data (bytes): The data to be decoded.

        Returns:
           T: The decoded data.
        """
        return bumble.decode(self.codec.decode(data))

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
            bumble.utils.standard_codecs.Codecs[codec.upper()] if isinstance(codec, str) else codec
            for codec
            in item
        ])) if item else cls()

__all__ = ['Pipeline']