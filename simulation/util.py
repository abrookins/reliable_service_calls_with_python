#!/usr/bin/env python
# encoding: utf-8
import redis


def redis_client():
    """Return a `redis.StrictRedis` with the correct db and port."""
    return redis.StrictRedis(host="redis", port=6379, db=0,
                             decode_responses=True)
