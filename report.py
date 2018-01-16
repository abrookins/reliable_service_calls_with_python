#!/usr/bin/env python
# encoding: utf-8
import falcon
import json
import logging
import redis
import sys


r = redis.StrictRedis(host="redis", port=6379, db=0)
log = logging.getLogger(__name__)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class ReportResource:
    """A resource that returns a report of all current simulation data.

    GET this endpoint to retrieve simulation data:

        $ curl -X GET "http://192.168.99.100:8004/report"

    Response:

        < HTTP/1.1 200 OK
        < Server: gunicorn/19.6.0
        < Date: Mon, 05 Sep 2016 21:55:21 GMT
        < Connection: close
        < content-length: 18
        < content-type: application/json; charset=UTF-8
        <
        * Closing connection 0
        {"report": {"stats.recommendations.get": 1, "stats.authorization.permission_denied": 1}}
    """

    def on_get(self, req, resp):
        """Return a report of all current stats."""
        keys = r.keys('stats\.*')
        resp.body = json.dumps({'report': {key.decode(): float(r.get(key).decode())
                                           for key in keys}})


api = falcon.API()
api.add_route('/report', ReportResource())
