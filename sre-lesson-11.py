import argparse
import time

import requests
from prometheus_client import start_http_server, Gauge, CollectorRegistry

ISS_API_URL = 'http://api.open-notify.org/iss-now.json'


class ISSMetrics:
    """
    ISS coordinates metric class.
    """
    def __init__(self, registry) -> None:
        self.iss_latitude_gauge = Gauge(
            'iss_latitude',
            'Current latitude of the ISS',
            registry=registry
        )
        self.iss_longitude_gauge = Gauge(
            'iss_longitude',
            'Current longitude of the ISS',
            registry=registry
        )

    def update_metrics(self, latitude, longitude) -> None:
        """
        Update metrics class method.
        """
        self.iss_latitude_gauge.set(latitude)
        self.iss_longitude_gauge.set(longitude)


def fetch_iss_location(metrics) -> None:
    """
    Get JSON response from static iss url and parse coordinates.
    """
    try:
        response = requests.get(ISS_API_URL)
        response.raise_for_status()

        data = response.json()
        latitude = float(data['iss_position']['latitude'])
        longitude = float(data['iss_position']['longitude'])
        metrics.update_metrics(latitude, longitude)

    except requests.exceptions.RequestException as e:
        print("Error:", e)

    except KeyError as e:
        print("JSON parse error:", e)


def main():
    parser = argparse.ArgumentParser(description='Run a Prometheus exporter for ISS position.')
    parser.add_argument(
        '--port',
        type=int,
        default=9280,
        help='Port to run the Prometheus exporter on (default: 9280)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=10,
        help='Interval in seconds between data fetches (default: 10)'
    )
    args = parser.parse_args()

    custom_registry = CollectorRegistry()
    iss_metrics = ISSMetrics(registry=custom_registry)
    start_http_server(args.port, registry=custom_registry)

    while True:
        fetch_iss_location(iss_metrics)
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
