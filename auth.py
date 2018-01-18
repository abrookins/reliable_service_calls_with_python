#!/usr/bin/env python
# encoding: utf-8
import falcon
import json
import redis
import uuid

from apiclient import ApiClient


r = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)
metrics = ApiClient('metrics')


class AuthenticationResource:
    """Verify an authentication token.

    POST to this endpoint to retrieve authentication details for a user.

        $ curl -v -H "Authorization: Token 0x132" -X POST "http://192.168.99.100:8000/authenticate"

    Response:

        < HTTP/1.1 200 OK
        < Server: gunicorn/19.6.0
        < Date: Mon, 05 Sep 2016 22:05:01 GMT
        < Connection: close
        < content-length: 114
        < content-type: application/json; charset=UTF-8
        <
        * Closing connection 0
        {"permissions": ["can_view_recommendations", "can_view_homepage"], "uuid": "f180f501-2378-4292-b364-d4a0d1b52c51"}

    Note: for the purposes of easier testing, this endpoint considers *all*
    tokens valid.
    """
    def on_post(self, req, resp):
        """Return authentication details if a valid token was provided."""
        token = req.get_header('Authorization')
        challenges = ['Token type="pudding"']

        if token is None:
            metrics.post('authentication.missing_auth_token')
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
