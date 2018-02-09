#!/usr/bin/env python
# encoding: utf-8
import datetime
import json
import logging
import time
import uuid

import falcon

from .redis_helpers import redis_client


METRICS_KEY = 'metrics'

redis = redis_client()
log = logging.getLogger(__name__)


class MetricsResource:
    """A resource that stores and returns application metrics.

    GET this endpoint to retrieve metrics:

        $ curl -X GET "http://192.168.99.100:8005/metrics"

    Response:

        < HTTP/1.1 200 OK
        < Server: gunicorn/19.6.0
        < Date: Mon, 05 Sep 2016 21:55:21 GMT
        < Connection: close
        < content-length: 18
        < content-type: application/json; charset=UTF-8
        <
        * Closing connection 0
        {
            "metrics": [
                [
                    "2018-01-22T04:41:44Z",
                    "authorization.authorization_success"
                ],
                [
                    "2018-01-22T04:41:44Z",
                    "authorization.authorization_success"
                ],
                [
                    "2018-01-22T04:41:44Z",
                    "recommendations.get"
                ],
                [
                    "2018-01-22T04:41:44Z",
                    "popular_items.get"
                ],
                [
                    "2018-01-22T04:41:44Z",
                    "homepage.get"
                ]
            ]
        }
    """

    def _unix_to_iso_8601(self, timestamp):
        """Make a UTC ISO-8601 timestamp from a UNIX timestamp."""
        return datetime.datetime.utcfromtimestamp(
            timestamp
        ).strftime('%Y-%m-%dT%H:%M:%SZ')

    def on_get(self, req, resp):
        """Return all metrics events.

        When returning metrics, metric keys are given to the client without
        their unique IDs. This is done for simpliciy, as the unique ID is
        not used by this simulation. Thus the return value is a list of pairs
        of the structure (timestamp, key), sorted by timestamp.
        """
        metrics = redis.zrange('metrics', 0, -1, withscores=True) or []

        # Strip the UUID of each event from the key.
        metrics = [(self._unix_to_iso_8601(score), key.split(':')[1])
                   for key, score in metrics]
        resp.body = json.dumps({'metrics': metrics})

    def on_post(self, req, resp):
        """Create a metrics event.

        Metrics are stored in Redis as a sorted set of (timestamp, id:key) pairs.
        We use a UUID as part of the key name rather than a timestamp in order to
        capture multiple keys submitted at the same time.
        """
        key = req.stream.read().decode()

        if not key:
            raise falcon.HTTPBadRequest('Metrics key required',
                                        'You must provide a metrics key in the request body')

        _id = str(uuid.uuid4())
        redis.zadd(METRICS_KEY, time.time(), '{}:{}'.format(_id, key))
        resp.status = falcon.HTTP_201

    def on_delete(self, req, resp):
        """Delete all current metrics."""
        redis.delete(METRICS_KEY)


api = falcon.API()
api.add_route('/metrics', MetricsResource())
