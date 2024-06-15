import bumble
import standard_codecs
import functools
import operator

class Pipeline:
    def __init__(self, codec: standard_codecs.Codec = standard_codecs.Codecs.NULL):
        self.codec = codec

    def encode[T](self, data: T) -> bytes:
        return self.codec.encode(bumble.encode(data))

    def decode[T](self, data: bytes) -> T:
        return bumble.decode(self.codec.decode(data))

    @classmethod
    def of(cls, *item) -> 'Pipeline':
        return cls(functools.reduce(operator.or_, [
            standard_codecs.Codecs[codec.upper()] if isinstance(codec, str) else codec
            for codec
            in item
        ]))
