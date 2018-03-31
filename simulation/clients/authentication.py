import pybreaker

from simulation.api_client import ApiClient

class AuthenticationClient(ApiClient):
    url = 'http://authentication:8000/authenticate'
    circuit_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)
