#!/usr/bin/env python
# encoding: utf-8
import falcon
import json
import logging
import redis
import statsd
import sys

from middleware import PermissionsMiddleware, FuzzingMiddleware

c = statsd.StatsClient('graphite', 2003)
r = redis.StrictRedis(host="redis", port=6379, db=0)
log = logging.getLogger(__name__)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class RecommendationsResource:
    """A resource that returns recommendations for a user.

    GET from the endpoint to see recommendations:

        $ curl -H "Authorization: Token 0x132" "http://192.168.99.100:8001/home"

    Response:

        < HTTP/1.1 200 OK
        < Server: gunicorn/19.6.0
        < Date: Mon, 05 Sep 2016 21:58:02 GMT
        < Connection: close
        < content-length: 48
        < content-type: application/json; charset=UTF-8
        <
        * Closing connection 0
        [12, 23, 100, 122, 220, 333, 340, 400, 555, 654]

    Note that the request must include an authentication token.
    """
    def _recommended_for_user(self, user_uuid):
        """Return items recommended for a user."""
        # Pretend we looked these numbers up by ``user_uuid``, probably in a
        # precomputed hash table (redis, etc.).
        return [12, 23, 100, 122, 220, 333, 340, 400, 555, 654]

    def on_get(self, req, resp):
        """Return recommendations for a user."""
        c.incr('recommendations.get')
        user_details = req.context['user_details']
        resp.body = json.dumps(self._recommended_for_user(user_details['uuid']))


api = falcon.API(middleware=[
    PermissionsMiddleware('can_view_recommendations'),
    FuzzingMiddleware()
])
api.add_route('/recommendations', RecommendationsResource())