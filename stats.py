#!/usr/bin/env python
# encoding: utf-8
import falcon
import json
import logging
import redis
import sys


r = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)
log = logging.getLogger(__name__)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class StatsResource:
    """A resource that returns all current simulation stats.

    GET this endpoint to retrieve simulation data:

        $ curl -X GET "http://192.168.99.100:8004/stats"

    Response:

        < HTTP/1.1 200 OK
        < Server: gunicorn/19.6.0
        < Date: Mon, 05 Sep 2016 21:55:21 GMT
        < Connection: close
        < content-length: 18
        < content-type: application/json; charset=UTF-8
        <
        * Closing connection 0
        {"stats": {"stats.recommendations.get": 1, "stats.authorization.permission_denied": 1}}
    """

    def on_get(self, req, resp):
        """Return all current stats."""
        stats = {key: int(value) for key, value in r.hgetall('stats').items()}
        resp.body = json.dumps({'stats': stats})

    def on_delete(self, req, resp):
        """Delete all current stats."""
        r.delete('stats')


api = falcon.API()
api.add_route('/report', StatsResource())
