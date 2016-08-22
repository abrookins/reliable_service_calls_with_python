#!/usr/bin/env python
# encoding: utf-8
import falcon
import requests
import statsd

c = statsd.StatsClient('graphite', 2003)


class PermissionsMiddleware(object):

    def __init__(self, permissions):
        self._required_permissions = permissions

    def process_request(self, req, resp):
        token = req.get_header('Authorization')
        challenges = ['Token type="chocolate"']

        if token is None:
            c.incr('recommendations.missing_auth_token')
            description = 'Please provide an auth token as part of the request.'

            raise falcon.HTTPUnauthorized('Auth token required',
                                          description,
                                          challenges,
                                          href='http://docs.example.com/auth')

        user_details = requests.post('http://authentication:8000/authenticate')

        if user_details.status_code == 400:
            c.incr('recommendations.permission_denied')
            description = 'The token was invalid.'

            raise falcon.HTTPUnauthorized('Invalid token',
                                          description,
                                          challenges,
                                          href='http://docs.example.com/auth')

        if not self._has_permission(user_details):
            c.incr('recommendations.permission_denied')
            description = 'You do not have permission to access this resource.'

            raise falcon.HTTPForbidden('Permission denied',
                                       description,
                                       href='http://docs.example.com/auth')

        c.incr('recommendations.authorization_success')
        req.context['user_details'] = user_details.json()

    def _has_permission(self, user_details):
        permissions = user_details.json().get('permissions', [])

        if self._required_permissions in permissions:
            return True

        return False
