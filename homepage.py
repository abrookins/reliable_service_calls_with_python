#!/usr/bin/env python
# encoding: utf-8
import falcon
import json

import pybreaker

from middleware import PermissionsMiddleware
from apiclient import ApiClient


recommended = ApiClient('recommendations')
popular = ApiClient('popular')

recommendations_breaker = pybreaker.CircuitBreaker(fail_max=1, reset_timeout=30)
popular_breaker = pybreaker.CircuitBreaker(fail_max=1, reset_timeout=30)


class HomepageResource:
    def on_get(self, req, resp):
        """Return data for the homepage."""
        auth_header = req.context.get('auth_header')
        recommendations = recommended.get().json()

        if not recommendations:
            recommendations = popular.get(headers=auth_header).json()

        if not recommendations:
            recommendations = []

        resp.body = json.dumps({
            'recommendations': recommendations
        })


api = falcon.API(middleware=[
    PermissionsMiddleware('can_view_homepage')
])
api.add_route('/home', HomepageResource())
