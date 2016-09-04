#!/usr/bin/env python
# encoding: utf-8
import random

from requests.packages.urllib3.util.retry import Retry


class JitteryRetry(Retry):
    """A Retry object that applies random jitter to exponential backoff rates.

    Based on: https://www.awsarchitectureblog.com/2015/03/backoff.html
    """
    def get_backoff_time(self):
        """Compute the current backoff with random jitter applied.

        :rtype: float
        """
        if self._observed_errors <= 1:
            return 0

        backoff_value = self.backoff_factor * (2 ** (self._observed_errors - 1))
        return min(self.BACKOFF_MAX, random.uniform(0.0, backoff_value))
