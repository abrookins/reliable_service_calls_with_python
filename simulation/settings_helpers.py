#!/usr/bin/env python
# encoding: utf-8
from .api_client import ApiClient
from .default_settings import DEFAULT_SETTINGS

_client_settings = None


def get_client_settings():
    global _client_settings
    defaults = DEFAULT_SETTINGS.copy()
    _client_settings = _client_settings \
                       or ApiClient('settings', defaults).get() \
                       or defaults
    return _client_settings
