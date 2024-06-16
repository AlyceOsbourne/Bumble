"""Everything contained in this module pertains to the codec itself."""
import functools

from bumble.codec import _encode, _decode
from bumble.constants import MODULE_MAPPING, REVERSE_MODULE_MAPPING
from bumble.exceptions import BumbleEncodeException, BumbleDecodeException
from bumble.helpers import _initialize_collection, _finalize_collection


def encode[T](data: T) -> bytes:
    """Encode Python object to bytes."""
    return _encode(data)


def decode[T](data: bytes | str) -> T:
    """Decode bytes or string to Python object."""
    if isinstance(data, bytes):
        data = data.decode()
    if not isinstance(data, str):
        raise BumbleDecodeException("Data must be a string or bytes")
    result, _ = _decode(data, 0)
    return result


################ HERE BE DRAGONS ################
########### No, Seriously, Don't Look ###########
@functools.lru_cache(1)
def _pickle_patch():
    """Patch pickle module to use Bumble encoding/decoding."""
    import pickle

    original_dumps = pickle.dumps  # type: ignore
    original_loads = pickle.loads  # type: ignore
    original_dump = pickle.dump  # type: ignore
    original_load = pickle.load  # type: ignore

    if not hasattr(original_dumps, '__wrapped__'):
        @functools.wraps(original_dumps)
        def do_encode(obj, **pickle_kwargs):
            try:
                return _encode(obj)
            except BumbleEncodeException:
                return original_dumps(obj, **pickle_kwargs)

        pickle.dumps = do_encode

    if not hasattr(original_loads, '__wrapped__'):
        @functools.wraps(original_loads)
        def do_decode(obj, **pickle_kwargs):
            try:
                return original_loads(obj, **pickle_kwargs)
            except pickle.UnpicklingError:
                return decode(obj)

        pickle.loads = do_decode

    if not hasattr(original_dump, '__wrapped__'):
        @functools.wraps(original_dump)
        def do_dumps(obj, file, **pickle_kwargs):
            try:
                file.write(_encode(obj))
            except BumbleEncodeException:
                return original_dump(obj, file, **pickle_kwargs)

        pickle.dump = do_dumps

    if not hasattr(original_load, '__wrapped__'):
        @functools.wraps(original_load)
        def do_loads(file, **pickle_kwargs):
            try:
                return decode(file.read())
            except BumbleDecodeException:
                return original_load(file, **pickle_kwargs)

        pickle.load = do_loads

    return pickle


@functools.lru_cache
def __getattr__(name):
    """
    Custom getattr for module-level attribute access.
    This monkey patches the pickle module if the user tries to import it from bumble.
    """
    if name == "pickle":
        return _pickle_patch()
    return globals().get(name)


# Abusing the linter, so it can correctly detect pickle when we import the patched module
if __debug__:
    import pickle

    del pickle  # noqa: E261
