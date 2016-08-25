#!/usr/bin/env python
# encoding: utf-8
import falcon
import pybreaker
import random
import statsd
import time

from apiclient import ApiClient


auth_client = ApiClient('authentication')
auth_breaker = pybreaker.CircuitBreaker(fail_max=1, reset_timeout=30)

c = statsd.StatsClient('graphite', 2003)


class FuzzingMiddleware:
    def process_request(self, req, resp):
        # Sometimes, the call takes 10 seconds. Oh, no!
        if random.randint(1, 3) == 1:
            time.sleep(5)


class PermissionsMiddleware:
    def __init__(self, permission):
        self._required_permission = permission

    def process_request(self, req, resp):
        token = req.get_header('Authorization')
        auth_headers = {'Authorization': token} if token else None

        try:
            auth_response = auth_breaker.call(auth_client.post, headers=auth_headers)
        except ConnectionError:
            c.incr('authorization.circuitbreaker.connection_error')
            return False
        except pybreaker.CircuitBreakerError:
            c.incr('authorization.circuitbreaker.error')
            return False

        if auth_headers:
            req.context['auth_header'] = auth_headers

        if auth_response.status_code == 401:
            raise falcon.HTTPUnauthorized('Auth token required',
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
        req.context['user_details'] = user_details

    def _has_permission(self, user_details):
        permissions = user_details.get('permissions', [])

        if self._required_permission in permissions:
            return True

        return False
