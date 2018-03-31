#!/usr/bin/env python
# encoding: utf-8
import json

from .redis_helpers import from_redis_hash, redis_client
from .default_settings import DEFAULT_SETTINGS

SETTINGS_KEY = 'settings'

_client_settings = None
redis = redis_client()


def get_client_settings():
    """Return the settings that ApiClient instances should use.

    Defaults to falcon.default_settings.DEFAULT_SETTINGS. Any setting changed
    via the Settings API overrides its default.
    """
    global _client_settings

    settings = DEFAULT_SETTINGS.copy()
    settings.update(from_redis_hash(redis.hgetall(SETTINGS_KEY) or {}))
    _client_settings = settings

    return _client_settings
