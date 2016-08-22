#!/usr/bin/env python
# encoding: utf-8

import falcon
import json
import statsd


c = statsd.StatsClient('graphite', 2003)


class PopularItemsResource:

    def on_get(self, req, resp):
        """Return yesterday's most popular items."""
        c.incr('popular_items.get')
        most_popular_yesterday = [1, 2, 3, 4, 5, 6, 7, 8 , 9, 10]
        resp.body = json.dumps(most_popular_yesterday)


api = falcon.API()
api.add_route('/popular', PopularItemsResource())
