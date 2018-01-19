#!/usr/bin/env python
# encoding: utf-8
import datetime
import json
import logging
import sys
import time

import falcon

from util import redis_client


redis = redis_client()
log = logging.getLogger(__name__)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class MetricsResource:
    """A resource that stores and returns application metrics.

    GET this endpoint to retrieve metrics:

        $ curl -X GET "http://192.168.99.100:8004/metrics"

    Response:

        < HTTP/1.1 200 OK
        < Server: gunicorn/19.6.0
        < Date: Mon, 05 Sep 2016 21:55:21 GMT
        < Connection: close
        < content-length: 18
        < content-type: application/json; charset=UTF-8
        <
        * Closing connection 0
        {"metrics": {"recommendations.get": 1, "authorization.permission_denied": 1}}
    """

    def _iso_timestamp(self, timestamp):
        """Make a UTC ISO-8601 datetime from a UNIX timestamp."""
        return datetime.datetime.utcfromtimestamp(
            timestamp
        ).strftime('%Y-%m-%dT%H:%M:%SZ')

    def on_get(self, req, resp):
        """Return all metrics."""
        metrics = [(key, self._iso_timestamp(score))
                   for key, score in redis.zrange('metrics', 0, -1, withscores=True)]
        resp.body = json.dumps({'metrics': metrics})

    def on_post(self, req, resp):
        """Create a metric.

        Metrics are stored in Redis as a sorted set of (timestamp, key) pairs.
        """
        key = req.stream.read()
        redis.zadd('metrics', time.time(), key)
        resp.status = falcon.HTTP_201

    def on_delete(self, req, resp):
        """Delete all current metrics."""
        redis.delete('metrics')


api = falcon.API()
api.add_route('/metrics', MetricsResource())
