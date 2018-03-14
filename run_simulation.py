#!/usr/bin/env python
# encoding: utf-8

import requests

from subprocess import run, PIPE

IP = run('docker-machine ip', shell=True, stdout=PIPE).stdout.strip().decode()
SETTINGS_URL = f"http://{IP}/settings"
HOME_URL = f"http://{IP}"
HEADERS = {
    'Authorization': 'Token 0x123'
}


def simulation_one():
    """Failure of an upstream service without circuit breakers, timeouts, or retries.
        Expected result: 0 requests served during outage
    """
    resp = requests.put(SETTINGS_URL, headers=HEADERS, json={
        'circuit_breakers': False,
        'timeout': 10,
        'retries': False,
        'outages': ['/recommendations']
    })

    print(resp.json())

    resp = requests.get(HOME_URL, headers=HEADERS)

    print(resp.json())

    run(f'wrk {HOME_URL} -H "Authorization: 0x123"', shell=True, stdout=PIPE).stdout.strip().decode()

if __name__ == '__main__':
    simulation_one()
