# Demonstrating Timeouts, Retries, Circuit Breakers, API Gateways, and Graceful Degradation with an Outage Simulator

This project is an outage simulator designed to demonstrate the effects of
timeouts, retries, circuit breakers, and other stability techniques in a
service-oriented system. The language used is Python, but the concepts
are language-agnostic.

The form of the demonstration is a set of backend web services against which
two common failure modes are simulated: socket errors when connecting to an
upstream service (e.g., due to misconfiguration) and slow response times (e.g.,
due to performance problems upstream).

The techniques demonstrated include:

* **Timeouts**: deadlines that network requests must meet, after which the program stops waiting
* **Retries with backoff and jitter**: attempts to retry a failed network request
* **Circuit breakers**: mechanisms that stop executing code after reaching a failure threshold
* **API gateway**: code that templates error handling around network requests
* **Graceful degradation**: falling back to a degraded state

Many of these concepts are based on Chapter 5, "Stability Patterns," of the
book *Release It!* by Michael Nygard.

The use of exponential backoff with "full jitter" when doing retries is based
on [*Exponential Backoff And Jitter*](https://www.awsarchitectureblog.com/2015/03/backoff.html),
published in the *AWS Architecture Blog*.


## Introducing the Demo System

The simulations run for the demonstration use the "homepage" service included in
this project. The homepage service acts as a composition layer that returns a
JSON response containing data needed for a client to render a user's theoretical
homepage:

* Popular items from the popularity service
* Recommended items from the recommendations service

(What these "items" are is left unspecified.)

The service requires an authentication token that is forwarded to a system that
authenticates the token and returns the user's permissions.

Here is an example request:

```
    $ curl -v -H "Authorization: Token 0x132" `docker-machine ip`\n

    < HTTP/1.1 200 OK
    < Server: gunicorn/19.6.0
    < Date: Mon, 05 Sep 2016 23:19:05 GMT
    < Connection: close
    < content-type: application/json; charset=UTF-8
    < content-length: 119
    <
    * Closing connection 0
    {"recommendations": [12, 23, 100, 122, 220, 333, 340, 400, 555, 654], "popular_items": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
```

As you can see, we get two lists, `recommendations` and `popular_items`.


## Running the Demo System

The demo system runs as a set of Docker containers defined in the
`docker-compose.yml` file.

You will need Docker installed to run the system. After installing Docker,
build the images and start the services with the following commands:

    $ docker-compose up

After all the containers are running, you should be able to make a request of
the homepage service:

    $ curl -v -H "Authorization: Token 0x132" `docker-machine ip`\n

If that doesn't work, try checking `docker-compose logs home` and
`docker-compose logs nginx` to see the service's logs.

You can see your Docker machine's IP address with the command `docker-machine
ip`. 


## Python Dependencies

You can install the Python dependencies for the project outside of Docker
containers by running `pip install -r requirements.txt`. The supported version
of Python is 3.6.4.


## Metrics and Graphs

Telegraf is configured to receive stats from the services sent via a `statsd`
library and send them to InfluxDB.

A Grafana instance should be running at `<your Docker machine's IP>:3000`,
e.g. http://192.168.99.100:3000.

You can see metrics in InfluxDB by logging into the Grafana instance and
creating a new dashboard. The default username and password for the Grafana
instance are are both 'admin'.

When you first login, you will need to configure an InfluxDB data source.
You can do so from the 'Home' screen, or from Configuration (the gear) -> 
Data Sources.

On the Data Sources / New page, choose 'InfluxDB' as the type.
The InfluxDB URL is `<your Docker machine's IP>:8086`, e.g. http://192.168.99.100:8086.
The access type is 'direct', no authentication is needed (leave Basic Auth
and With Credentials unchecked). Set the "Database" field under InfluxDB Details
to "telegraf" and leave the "User" and "Password" fields blank.

That should work -- test it with the "Save & Test" button.


## Running the Simulation

There is an included Python script that will set up the conditions for an
outage simulation and then run it. The script requires that `wrk` is installed
on your computer. On macOS, this is available via Homebrew, e.g. `brew install
wrk`.

The script takes various options that will control the type of simulation run.
E.g., to simulate an outage during which requests to an upstream service will
result in socket errors, run:

    python run_simulation.py outage --duration 30

To simulate a performance issue in an upstream service, run:

    python run_simulation.py performance --duration 30

To simulate the same outage, but with one-second timeouts, run:

    python run_simulation.py performance --duration 30 --timeout 1

To do the same, but with one-second timeouts _and_ circuit breakers, run:

    python run_simulation.py performance --duration 30 --timeout 1 --circuit-breakers

To see the mess that retries can cause, run:

    python run_simulation.py performance --duration 30 --timeout 3 --retries

You can see all the script's options by running `python run_simulation.py --help`.


## Troubleshooting

Sometimes, weird things happen with the Docker containers. These are pretty standard
Docker steps I use with Docker Toolbox (I tried Docker for Mac and it wasn't for me):

- What's my machine's IP? `docker-machine ip`
- Is the machine even on? `docker-machine start default`
- Make sure bash/zsh knows where to find the Docker machine `eval $(docker-machine env default)`
- Is everything running? `docker-compose ps`
- Powercycle it `docker compose restart`
- Damn it all (`docker-compose stop`, `docker-compose rm`, `docker-compose up` -- remove the images and rebuild)
- Repeat.....
