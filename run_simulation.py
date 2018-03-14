#!/usr/bin/env python
# encoding: utf-8

import requests

from subprocess import run, PIPE

IP = run('docker-machine ip', shell=True, stdout=PIPE).stdout.strip().decode()
URL = f"http://{IP}/settings"
HEADERS = {
    'Authorization': 'Token 0x132'
}


def simulation_one():
    """Failure of an upstream service without circuit breakers, timeouts, or retries.
        Expected result: 0 requests served during outage
    """
    resp = requests.put(URL, headers=HEADERS, json={
        'circuit_breakers': False,
        'timeouts': False,
        'retries': False,
        'outages': ['/recommendations']
    })

    print(resp.json())

    # run('wrk ', shell=True, stdout=PIPE).stdout.strip().decode()

if __name__ == '__main__':
    simulation_one()
