#!/usr/bin/env python
# encoding: utf-8
import json
import logging
import falcon
import redis
import sys

import apiclient

r = redis.StrictRedis(host="redis", port=6379, db=0)
log = logging.getLogger(__name__)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class OutageResource:
    """A resource that simulates an outage.

    POST to this endpoint to toggle the outage state for a given service:

        $ curl -X POST "http://192.168.99.100:8004/outage/recommendations"

    Response:

        < HTTP/1.1 200 OK
        < Server: gunicorn/19.6.0
        < Date: Mon, 05 Sep 2016 21:55:21 GMT
        < Connection: close
        < content-length: 18
        < content-type: application/json; charset=UTF-8
        <
        * Closing connection 0
        {"outage": "true"}
    """
    def on_post(self, req, resp, service):
        """Toggle the outage condition for the given service."""
        if service not in apiclient.urls.keys():
            raise falcon.HTTPNotFound

        key = '/{}'.format(service)
        outage = r.get(key)

        if outage:
            outage = outage.decode('utf-8')
        if outage == 'true':
            new_value = 'false'
        else:
            new_value = 'true'

        r.set(key, new_value.encode('utf-8'))
        resp.body = json.dumps({'outage': new_value})


api = falcon.API()
api.add_route('/outage/{service}', OutageResource())
