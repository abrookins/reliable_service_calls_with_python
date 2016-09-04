#!/usr/bin/env python
# encoding: utf-8
import falcon
import json
import uuid
import statsd


c = statsd.StatsClient('graphite', 2003)


class AuthenticationResource:
    def on_post(self, req, resp):
        """Return authentication details if a valid token was provided."""
        token = req.get_header('Authorization')
        challenges = ['Token type="pudding"']

        if token is None:
            c.incr('authentication.missing_auth_token')
            description = 'Please provide an auth token as part of the request.'

            raise falcon.HTTPUnauthorized('Auth token required',
                                          description,
                                          challenges,
                                          href='http://docs.example.com/auth')

        user_details = {
            'uuid': str(uuid.uuid4()),
            'permissions': ['can_view_recommendations', 'can_view_homepage']
        }

        resp.body = json.dumps(user_details)


api = falcon.API()
api.add_route('/authenticate', AuthenticationResource())
