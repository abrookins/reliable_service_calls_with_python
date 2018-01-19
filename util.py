#!/usr/bin/env python
# encoding: utf-8
import redis


def redis_client():
    return redis.StrictRedis(host="redis", port=6379, db=0,
                             decode_responses=True)
