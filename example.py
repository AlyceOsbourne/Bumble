"""Example of using Bumble to encode various kinds of common patterns."""

import dataclasses
import typing
import bumble
import pickle
from bumble.utils.pipeline import Pipeline


def validate(obj):
    """Validate the metadata."""
    for name, annotation in getattr(obj, '__annotations__', {}).items():
        if type(annotation) is typing._AnnotatedAlias:  # noqa
            for validator in annotation.__metadata__:
                if not isinstance(validator, tuple):
                    continue
                assert validator[0](getattr(obj, name)), validator[1]


@dataclasses.dataclass
class Metadata:
    """Metadata for a plugin."""
    id: typing.Annotated[
        str,
        'A unique identifier for the plugin. Must be a valid Python identifier.',
        (lambda x: x.isidentifier(), 'Must be a valid Python identifier'),
        (lambda x: len(x) > 0, 'Must not be empty'),
        (lambda x: len(x) < 100, 'Must be less than 100 characters')
    ]
    name: typing.Annotated[
        str,
        'Human readable name of the plugin.',
        (lambda x: x.isprintable(), 'Must be a printable string'),
        (lambda x: len(x) > 0, 'Must not be empty'),
        (lambda x: len(x) < 100, 'Must be less than 100 characters')
    ]
    version: typing.Annotated[
        str,
        'Version of the plugin.',
        (lambda x: x.isprintable(), 'Must be a printable string'),
        (lambda x: len(x) > 0, 'Must not be empty'),
        (lambda x: x.count('.') in [2, 3], 'Version string must be formatter as X.Y.Z[.W]'),
    ]
    description: typing.Annotated[
        str,
        'Description of the plugin.',
        (lambda x: x.isprintable(), 'Must be a printable string'),
        (lambda x: len(x) > 0, 'Must not be empty'),
        (lambda x: len(x) < 1000, 'Must be less than 1000 characters')
    ]

    def __post_init__(self):
        """Validate the metadata."""
        validate(self)

metadata = Metadata('id', 'name', '1.1.1', 'description')

bumbled = bumble.encode(metadata)
pickled = pickle.dumps(metadata)

pipe = Pipeline.of("zlib", "b85")
encoded = pipe.encode(metadata)

print("Encoded with pickle", pickled, sep='\n', end='\n\n')

print("Encoded with pure Bumble", bumbled, sep='\n', end='\n\n')

print(f"Encoded with Bumble pipeline {pipe!r}", encoded, sep='\n')
