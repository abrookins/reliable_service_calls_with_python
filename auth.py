#!/usr/bin/env python
# encoding: utf-8
import falcon
import json
import random
import time
import uuid


class AuthenticationResource:
    def on_post(self, req, resp):
        """Return authentication details if a valid token was provided."""
        # Sometimes, this call takes 20 seconds. Oh, no!
        if random.randint(1, 3) == 1:
            time.sleep(10)

        user_details = {
            'uuid': str(uuid.uuid4()),
            'permissions': ['can_view_recommendations']
        }

        resp.body = json.dumps(user_details)


api = falcon.API()
api.add_route('/authenticate', AuthenticationResource())
