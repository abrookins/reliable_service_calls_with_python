#!/usr/bin/env python
# encoding: utf-8
import falcon
import json

import pybreaker

from middleware import PermissionsMiddleware
from apiclient import ApiClient


rec_client = ApiClient('recommendations')
popularity_client = ApiClient('popular')


class HomepageResource:
    def on_get(self, req, resp):
        """Return data for the homepage."""
        auth_header = req.context.get('auth_header')

        try:
            request = rec_client.get(headers=auth_header)
            recommendations = request.json()
        except ConnectionError:
            request = popularity_client.get(headers=auth_header)
            recommendations = request.json()
        except (pybreaker.CircuitBreakerError, Exception):
            recommendations = []

        resp.body = json.dumps({
            'recommendations': recommendations
        })


api = falcon.API(middleware=[
    PermissionsMiddleware('can_view_homepage')
])
api.add_route('/home', HomepageResource())
