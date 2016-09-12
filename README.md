# Reliable service calls with Python

This project demonstrates stability patterns that will make your service calls
in Python more reliable.

The form of the demonstration is a set of backend web services against which
various common failure modes were simulated. For example, total failure of an
upstream web service.

The patterns demonstrated include, with brief definitions (you can find better definitions elsewhere):

* **Circuit breakers**: mechanisms that stop executing code paths after calls reach a failure threshold
* **Timeouts**: deadlines that our network requests must meet, after which the program stops waiting
* **Retries with exponential backoff and random jitter**: attempts by the program to try a failed network request again
* **Graceful degradation**: falling back to a degraded state; i.e., returning partial data
* **"Generic Gateway"**: a collection of code that templates error handling, especially around network requests

The "generic Gateway" and "circuit breaker" pattern are based on Chapter 5,
"Stability Patterns," of the book *Release It!* by Michael Nygard.

The idea to use exponential backoff with "jitter" is based on [*Exponential
Backoff And Jitter*](https://www.awsarchitectureblog.com/2015/03/backoff.html),
published in the *AWS Architecture Blog*.

## Introducing the demo system

The simulations run to produce this document use the "homepage" service included
in this project. The homepage service acts as a composition layer that returns a
JSON response containing data needed for a client to render a user's theoretical
homepage:

* Popular items (from the popularity service)
* Items recommended for this user (from the recommendations service)

(What these items are is unspecified.)

The service requires a token that is forwarded to an authentication system that
returns the user's permissions.

Here is an example request made of this service:

```
    $ curl -v -H "Authorization: Token 0x132" "http://192.168.99.100:8001/home"

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

As you can see, we get two lists: 'recommendations' and 'popular_items.'

## Method of inquiry

This document will proceed through a series of simulations, starting with the
total failure of an upstream service. Each simulation will give us a chance to
see Python code examples related to the pattern, and to see how the pattern
behaves under specific failure conditions.

With those introductions out of the way, let's start simulating!

## Simulation 1: total failure of an upstream service with graceful degradation (recommendations)

In this simulation, our homepage service is humming along, serving popularity
and recommendations data it pulled from two upstream services, when suddenly,
the upstream recommendations service stops responding.

Let's look at some graphs of data generated during the outage:

![Graph showing the recommendations service outage](images/outage_simulation.png)

The graph shows a timeline of events related to the outage:

1. The homepage service is handling steady traffic
2. An outage begins: the recommendations service stops working; homepage service availability plummets
3. Circuit breakers around the recommendations service open
    * Homepage service availability jumps back up, handling more traffic than before the outage
    * Recommendations circuit breakers report connection errors
4. The recommendations service comes back online; gradually the homepage service begins using it
8. All of the recommendations circuit breakers close, and normal operation resumes

*Very interesting, but I have questions*, you might be thinking! Here are a few
worth pondering:

### Why did homepage availability drop at the start of the outage, and what can we do about that?

The short drop in availability reflects the system trying, and failing, to
handle connection errors to the upstream recommendations service.

The homepage service's connection to the recommendations service uses the
`ApiClient` class. `ApiClient` applies timeouts, exponential retries with random
jitter, and circuit breakers to all network requests made by services in the
project.

In this case, network requests from the homepage service to the recommendations
service began to fail, generating errors. Retries and timeouts couldn't help
here -- the recommendations service failed 100% of the time.

Without timeouts or circuit breakers, homepage availability would have dropped
until the outage was over. But that's not what happened...

### What caused the circuit breakers to open?

Circuit breakers saved the homepage service: when they opened, the service
stopped trying to get recommendations and instead degraded to only providing
popular items.

But what caused the circuit breakers to open?

### Why, after the circuit breakers opened, did homepage availability get better than before the outage started?
### If the circuit breakers were open, why did we see connection errors during the outage?


## Simulating total failure of a dependent service without graceful degradation (authentication)

## Simulating dependent service non-total failure (performance problems)

## Simulating too many retries

