#!/bin/bash

if [ "$1" = '--initialize' ]; then
    docker-machine start default
    eval $(docker-machine env default)
    docker-compose build
    docker-compose up authentication recommendations homepage popular settings redis nginx grafana influxdb telegraf
fi

IP=`docker-machine ip`


# Simulation: Failure of an upstream service without circuit breakers, timeouts, or retries.
#   - 0 requests served during outage

curl -X PUT -H "Authorization: Token 0x132" -H "CONTENT-TYPE: application/json" \
    -d '{
        "circuit_breakers": false,
        "timeouts": false,
        "retries": false,
        "outages": ["/recommendations"]
      }' "$IP/settings"

echo

curl -H "Authorization: Token 0x132" "$IP/"

# Simulation: Failure of an upstream service without circuit breakers, timeouts, or fallback data, but with retries
#   - 0 requests served during outage, more errors

# Simulation: Failure of an upstream service with timeouts but no circuit breakers or fallback data
#   - requests served during outage, but all 500s (timeouts, no fallback data)

# Simulation: Failure of an upstream service with timeouts and fallback data, but no circuit breakers
#   - requests served during an outage, some errors (because no circuit breakers)

# Simulation: Failure of an upstream service with circuit breakers, timeouts, and fallback data
#   - requests served during outage

# Simulation: Non-total failure of an upstream service (performance problems) with breakers, timeouts, and fallback data
#   - requests served during outage, with highs and lows
