#!/usr/bin/env python
# encoding: utf-8
import falcon
import logging
import redis
import statsd
import time
import sys

from apiclient import ApiClient


auth_client = ApiClient('authentication')
c = statsd.StatsClient('graphite', port=2003)
r = redis.StrictRedis(host="redis", port=6379, db=0)
log = logging.getLogger(__name__)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class FuzzingMiddleware:
    """Middleware that simulates network latency.

    If we are in a simulated outage condition, the wrapped endpoint responds
    with a three second delay, which should exhaust the timeouts that all
    clients use.
    """
    def process_request(self, req, resp):
        outage = r.get(req.path)
        if outage:
            outage = outage.decode('utf-8')
        if outage == 'true':
            log.info('Delaying response time: {}'.format(outage))
            time.sleep(5)


class PermissionsMiddleware:
    """Middleware that requires a given permission.

    This middleware should receive a ``permission`` string on init,
    which identifies a single permission, as a string, that the
    user must possess to access the wrapped endpoint.
    """
    def __init__(self, permission):
        self._required_permission = permission

    def process_request(self, req, resp):
        token = req.get_header('Authorization')

        if not token:
            raise falcon.HTTPUnauthorized('Auth token required',
                                          '',
                                          '',
                                          href='http://docs.example.com/auth')

        auth_headers = {'Authorization': token}
        auth_response = auth_client.post(headers=auth_headers)

        if not auth_response:
            raise falcon.HTTPInternalServerError('Server error', 'There was a server error')

        if auth_response.status_code == 401:
            raise falcon.HTTPUnauthorized('Authorization failed',
                                          '',
                                          '',
                                          href='http://docs.example.com/auth')

        user_details = auth_response.json()

        if not self._has_permission(user_details):
            c.incr('authorization.permission_denied')
            description = 'You do not have permission to access this resource.'

            raise falcon.HTTPForbidden('Permission denied',
                                       description,
                                       href='http://docs.example.com/auth')

        c.incr('authorization.authorization_success')

        req.context['auth_header'] = auth_headers
        req.context['user_details'] = user_details

    def _has_permission(self, user_details):
        permissions = user_details.get('permissions', [])

        if self._required_permission in permissions:
            return True

        return False