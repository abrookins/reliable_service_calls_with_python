#!/usr/bin/env python
# encoding: utf-8
import random

from requests.packages.urllib3.util.retry import Retry


class RetryWithFullJitter(Retry):
    """A Retry object that applies random "full" jitter to backoff rates.

    Based on: https://www.awsarchitectureblog.com/2015/03/backoff.html
    """
    def get_backoff_time(self):
        value = super().get_backoff_time()
        return random.uniform(0.0, value)
