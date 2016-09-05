#!/usr/bin/env python
# encoding: utf-8
import falcon
import json
import statsd

from middleware import PermissionsMiddleware
from apiclient import ApiClient


c = statsd.StatsClient('graphite', 8125)
recommended = ApiClient('recommendations')
popular = ApiClient('popular')


class HomepageResource:
    """A resource that returns data for a user's homepage.

    GET from this endpoint to retrieve homepage data:

        $ curl -v -H "Authorization: Token 0x132" "http://192.168.99.100:8001/home"

    Response:

        < HTTP/1.1 200 OK
        < Server: gunicorn/19.6.0
        < Date: Mon, 05 Sep 2016 23:19:05 GMT
        < Connection: close
        < content-type: application/json; charset=UTF-8
        < content-length: 119
        <
        * Closing connection 0
        {"recommendations": [12, 23, 100, 122, 220, 333, 340, 400, 555, 654], "popular_items": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}

    Note that the request must include an authentication token.
    """
    def on_get(self, req, resp):
        """Return data for the homepage."""
        auth_header = req.context.get('auth_header')
        recommendations = recommended.get(headers=auth_header)
        recommendations = recommendations.json() if recommendations else []
        popular_items = popular.get(headers=auth_header)
        popular_items = popular_items.json() if popular_items else []

        resp.body = json.dumps({
            'recommendations': recommendations,
            'popular_items': popular_items
        })

        c.incr('homepage.get')


api = falcon.API(middleware=[
    PermissionsMiddleware('can_view_homepage')
])
api.add_route('/home', HomepageResource())
