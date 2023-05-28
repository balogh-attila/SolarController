"""InfluxDB Handler module."""
import logging
import os

from influxdb import InfluxDBClient


class InfluxDBHandler(object):
    """InfluxDB Handler class."""

    ENABLED = os.getenv('INFLUX', 'yes').lower() in ['true', '1', 'y', 'yes']
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', 8086)
    DB_NAME = os.getenv('DB_NAME', 'solar')
    DB_USER = os.getenv('DB_USER', 'solar')
    DB_PASS = os.getenv('DB_PASS', 'verysecret')

    db = None       # holder property for InfluxDB connenction

    log = logging.getLogger(__name__)

    def __init__(self):
        """Initialization of InfluxDB connection in constructor."""
        if self.ENABLED:
            self.log.info("Open InfluxDB connection: %s", self.DB_NAME)
            self.db = InfluxDBClient(
                self.DB_HOST,
                self.DB_PORT,
                self.DB_USER,
                self.DB_PASS,
                self.DB_NAME
        )

    def write_measurements(self, data, measurement):
        """Write inverter statistics."""
        if self.db != None:
            point = dict()
            point['measurement'] = measurement
            point['fields'] = data
            self.log.debug("InfluxDB - write data points: {%s}", point)
            self.db.write_points([point])
