import pybreaker

from simulation.api_client import ApiClient


class RecommendationsClient(ApiClient):
    url = 'http://recommendations:8002/recommendations'
    circuit_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)
