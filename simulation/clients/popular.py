import pybreaker

from simulation.api_client import ApiClient

class PopularItemsClient(ApiClient):
    url = 'http://popular:8003/popular_items'
    circuit_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)

