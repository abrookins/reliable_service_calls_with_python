#!/usr/bin/env python
# encoding: utf-8
import json
import logging

import falcon

from .redis_helpers import redis_client, from_redis_hash
from .settings_helpers import DEFAULT_SETTINGS

SETTINGS_KEY = 'settings'

OUTAGES_KEY = 'outages'

VALID_SETTINGS = {
    OUTAGES_KEY,
    'circuit_breakers',
    'timeouts',
    'retries'
}

log = logging.getLogger(__name__)

redis = redis_client()


class SettingsResource:
    """A resource that stores settings for the current simulation.

    PUT to this endpoint to replace the simulation's settings with new ones.
    E.g.:

        $ curl -X PUT "http://192.168.99.100:8004/settings" \
                -d '{"outages": ["/recommendations"]}'

    Response:

        < HTTP/1.1 200 OK
        < Server: gunicorn/19.6.0
        < Date: Mon, 05 Sep 2016 21:55:21 GMT
        < Connection: close
        < content-length: 18
        < content-type: application/json; charset=UTF-8
        <
        * Closing connection 0
        {"outages": ["/recommendations"]}

    Note: 'outages' is the only supported setting for now.
    """

    def on_get(self, req, resp):
        """Return the current simulation settings."""
        settings = DEFAULT_SETTINGS.copy()
        settings.update(from_redis_hash(redis.hgetall(SETTINGS_KEY) or {}))
        resp.body = json.dumps(settings)

    def on_put(self, req, resp):
        """Replace current simulation settings values."""
        try:
            settings = json.loads(req.stream.read()) or {}
        except (TypeError, json.JSONDecodeError):
            raise falcon.HTTPBadRequest(
                'Bad request',
                'Request body was not valid JSON')

        if not VALID_SETTINGS & set(settings.keys()):
            raise falcon.HTTPBadRequest(
                'Bad request',
                'Valid settings are: {}'.format(', '.join(VALID_SETTINGS)))

        if OUTAGES_KEY in settings:
            redis.delete(OUTAGES_KEY)
            for path in settings[OUTAGES_KEY]:
                redis.sadd(OUTAGES_KEY, path)
        else:
            redis.delete(OUTAGES_KEY)

        settings_hash = {k: v for k, v in settings.items() if k != OUTAGES_KEY}

        if settings_hash:
            redis.hmset(SETTINGS_KEY, settings_hash)
        else:
            redis.delete(SETTINGS_KEY)

        resp.body = json.dumps(settings)


api = falcon.API()
api.add_route('/settings', SettingsResource())
