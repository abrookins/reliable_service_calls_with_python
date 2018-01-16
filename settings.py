#!/usr/bin/env python
# encoding: utf-8
import json
import logging
import sys

import falcon
import redis

import apiclient

r = redis.StrictRedis(host="redis", port=6379, db=0)
log = logging.getLogger(__name__)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class SettingsResource:
    """A resource that stores settings for the current simulation.

    PUT to this endpoint to replace the simulation's settings with new ones.
    E.g.:

        $ curl -X PUT "http://192.168.99.100:8004/settings" {"outages": ["/recommendations"]}

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
    OUTAGES_KEY = 'outages'

    def on_put(self, req, resp):
        """Replace current simulation settings values."""
        try:
            settings = json.loads(req.stream.read())
        except (TypeError, json.JSONDecodeError):
            raise falcon.HTTPBadRequest('Bad request', 'Request body was not valid JSON')

        if self.OUTAGES_KEY not in settings:
            raise falcon.HTTPBadRequest('Bad request', 'Valid settings are: "outages"')

        r.delete(self.OUTAGES_KEY)

        for path in settings['outages']:
            r.sadd(self.OUTAGES_KEY, path)

        resp.body = json.dumps(settings)


api = falcon.API()
api.add_route('/settings', SettingsResource())
