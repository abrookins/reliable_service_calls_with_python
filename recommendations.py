#!/usr/bin/env python
# encoding: utf-8
import falcon
import json
import statsd

from middleware import PermissionsMiddleware

c = statsd.StatsClient('graphite', 2003)


class RecommendationsResource:

    def on_get(self, req, resp):
        """Return recommendations for a user.

        If the authentication service is down, fall back to returning
        yesterday's most popular items.
        """
        c.incr('recommendations.get')
        user_details = req.context['user_details']
        resp.body = json.dumps(self._recommended_for_user(user_details['uuid']))

    def _recommended_for_user(self, user_uuid):
        """Return items recommended for a user."""
        # Pretend we looked these numbers up by ``user_uuid``, probably in a
        # precomputed hash table (redis, etc.).
        return [12, 23, 100, 122, 220, 333, 340, 400, 555, 654]


api = falcon.API(middleware=[
    PermissionsMiddleware('can_view_recommendations')
])
api.add_route('/recommendations', RecommendationsResource())