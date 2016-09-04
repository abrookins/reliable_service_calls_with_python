#!/usr/bin/env python
# encoding: utf-8
import falcon
import json

import pybreaker

from middleware import PermissionsMiddleware
from apiclient import ApiClient


recommended = ApiClient('recommendations')
popular = ApiClient('popular')


class HomepageResource:
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


api = falcon.API(middleware=[
    PermissionsMiddleware('can_view_homepage')
])
api.add_route('/home', HomepageResource())
