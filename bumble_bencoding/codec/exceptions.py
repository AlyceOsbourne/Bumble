"""Exceptions for Bumble codec."""
import types

BumbleEncodeException = types.new_class('BumbleEncodeException', (Exception,))
BumbleDecodeException = types.new_class('BumbleDecodeException', (Exception,))

__all__ = ['BumbleEncodeException', 'BumbleDecodeException']
