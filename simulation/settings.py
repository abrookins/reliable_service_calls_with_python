#!/usr/bin/env python
# encoding: utf-8
import json
import logging

import falcon

from .redis_helpers import redis_client, from_redis_hash
SETTINGS_KEY = 'settings'

OUTAGES_KEY = 'outages'

PERFORMANCE_PROBLEMS_KEY = 'performance_problems'

VALID_SETTINGS = {
    OUTAGES_KEY,
    PERFORMANCE_PROBLEMS_KEY,
    'circuit_breakers',
    'timeout',
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
    """
    def _parse_settings(self, req):
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

        return settings

    def on_get(self, req, resp):
        """Return the current simulation settings."""
        settings = from_redis_hash(redis.hgetall(SETTINGS_KEY) or {})
        outages = list(redis.smembers(OUTAGES_KEY) or [])
        perf_problems = list(redis.smembers(PERFORMANCE_PROBLEMS_KEY) or [])

        if outages:
            settings[OUTAGES_KEY] = outages

        if perf_problems:
            settings[PERFORMANCE_PROBLEMS_KEY] = perf_problems

        resp.body = json.dumps(settings)

    def on_put(self, req, resp):
        """Replace current simulation settings."""
        settings = self._parse_settings(req)

        if OUTAGES_KEY in settings:
            redis.delete(OUTAGES_KEY)
            for path in settings[OUTAGES_KEY]:
                redis.sadd(OUTAGES_KEY, path)

        if PERFORMANCE_PROBLEMS_KEY in settings:
            redis.delete(PERFORMANCE_PROBLEMS_KEY)
            for path in settings[PERFORMANCE_PROBLEMS_KEY]:
                redis.sadd(PERFORMANCE_PROBLEMS_KEY, path)

        new_settings = {k: v for k, v in settings.items() if k != OUTAGES_KEY}

        if new_settings:
            redis.hmset(SETTINGS_KEY, new_settings)

        if OUTAGES_KEY in settings:
            new_settings[OUTAGES_KEY] = list(redis.smembers(OUTAGES_KEY) or [])

        if PERFORMANCE_PROBLEMS_KEY in settings:
            new_settings[PERFORMANCE_PROBLEMS_KEY] = list(
                redis.smembers(PERFORMANCE_PROBLEMS_KEY) or [])

        resp.body = json.dumps(new_settings)

    def on_patch(self, req, resp):
        """Partially update the current simulation settings."""
        settings = self._parse_settings(req)

        if OUTAGES_KEY in settings:
            redis.delete(OUTAGES_KEY)
            for path in settings[OUTAGES_KEY]:
                redis.sadd(OUTAGES_KEY, path)

        if PERFORMANCE_PROBLEMS_KEY in settings:
            redis.delete(PERFORMANCE_PROBLEMS_KEY)
            for path in settings[PERFORMANCE_PROBLEMS_KEY]:
                redis.sadd(PERFORMANCE_PROBLEMS_KEY, path)

        current_settings = from_redis_hash(redis.hgetall(SETTINGS_KEY) or {})
        new_settings = {k: v for k, v in settings.items() if k != OUTAGES_KEY}

        if new_settings:
            current_settings.update(new_settings)
            redis.hmset(SETTINGS_KEY, current_settings)

        if OUTAGES_KEY in settings:
            current_settings[OUTAGES_KEY] = list(redis.smembers(OUTAGES_KEY) or [])

        if PERFORMANCE_PROBLEMS_KEY in settings:
            current_settings[PERFORMANCE_PROBLEMS_KEY] = list(
                redis.smembers(PERFORMANCE_PROBLEMS_KEY) or [])

        resp.body = json.dumps(current_settings)


api = falcon.API()
api.add_route('/settings', SettingsResource())
