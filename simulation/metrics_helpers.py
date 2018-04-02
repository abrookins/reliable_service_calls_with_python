import statsd
import simulation


class StatsClient:
    def __init__(self, testing):
        if testing:
            statsd.Connection.set_defaults(host='localhost', port=8125, sample_rate=1, disabled=True)
        else:
            statsd.Connection.set_defaults(host='telegraf', port=8125, sample_rate=1)

    def incr(self, key):
        counter = statsd.Counter(key)
        counter += 1


def metrics_client():
    return StatsClient(simulation.TESTING)
