#!/usr/bin/env python
# encoding: utf-8
import redis
import fakeredis
import simulation


def from_redis_hash(hash):
    return {k: from_redis_value(v) for k, v in hash.items()}


def from_redis_value(value):
    if value == 'True':
        val = True
    elif value == 'False':
        val = False
    else:
        val = value
    return val


def redis_client():
    """Return a `redis.StrictRedis` with the correct db and port."""
    if simulation.TESTING:
        return fakeredis.FakeStrictRedis(decode_responses=True)

    return redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)
