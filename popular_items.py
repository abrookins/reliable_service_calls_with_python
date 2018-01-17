#!/usr/bin/env python
# encoding: utf-8

import falcon
import json
import redis

from middleware import FuzzingMiddleware


r = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)


class PopularItemsResource:
    """A resource that returns popular items.

    GET from this endpoint to receive a list of popular items:

        $ curl -v -H "Authorization: Token 0x132" "http://192.168.99.100:8003/popular_items"

    Response:

        < HTTP/1.1 200 OK
        < Server: gunicorn/19.6.0
        < Date: Mon, 05 Sep 2016 23:14:47 GMT
        < Connection: close
        < content-type: application/json; charset=UTF-8
        < content-length: 31
        <
        * Closing connection 0
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    """
    def on_get(self, req, resp):
        """Return yesterday's most popular items."""
        r.hincrby('stats', 'popular_items.get')
        most_popular_yesterday = [1, 2, 3, 4, 5, 6, 7, 8 , 9, 10]
        resp.body = json.dumps(most_popular_yesterday)


api = falcon.API(middleware=[
    FuzzingMiddleware()
])
api.add_route('/popular_items', PopularItemsResource())
