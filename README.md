# Reliable service calls with Python

The example code within this project demonstrates how to use core stability
patterns to make service calls in Python more reliable. These patterns include:

* Using the Circuit Breaker pattern
* Using timeouts
* Using retries with incremental backoff and random jitter (based on:
https://www.awsarchitectureblog.com/2015/03/backoff.html)

This project is based heavily on Chapter 5, "Stability Patterns," of the book
*Release It!* by Michael Nygard.


## Preview

![Graphs during an outage simulation](images/outage_simulation.png)
