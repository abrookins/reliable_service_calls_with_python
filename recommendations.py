#!/usr/bin/env python
# encoding: utf-8
import falcon
import json
import logging
import redis
import statsd

from middleware import PermissionsMiddleware, FuzzingMiddleware

c = statsd.StatsClient('graphite', 2003)

r = redis.StrictRedis(host="redis", port=6379, db=0)

log = logging.getLogger(__name__)


class RecommendationsResource:
    def _recommended_for_user(self, user_uuid):
        """Return items recommended for a user."""
        # Pretend we looked these numbers up by ``user_uuid``, probably in a
        # precomputed hash table (redis, etc.).
        return [12, 23, 100, 122, 220, 333, 340, 400, 555, 654]

    def on_get(self, req, resp):
        """Return recommendations for a user.

        If the authentication service is down, fall back to returning
        yesterday's most popular items.
        """
        c.incr('recommendations.get')
        user_details = req.context['user_details']
        resp.body = json.dumps(self._recommended_for_user(user_details['uuid']))

    def on_post(self, req, resp):
        """Toggle the outage condition."""
        c.incr('recommendations.post')
        key = req.path
        outage = r.get(key)
        if outage:
            outage = outage.decode('utf-8')
        log.error(outage)
        if outage == 'true':
            new_value = 'false'
        else:
            new_value = 'true'
        r.set(key, new_value.encode('utf-8'))
        resp.body = json.dumps({'outage': new_value})

api = falcon.API(middleware=[
    PermissionsMiddleware('can_view_recommendations'),
    FuzzingMiddleware()
])
api.add_route('/recommendations', RecommendationsResource())