#!/usr/bin/env python3
"""Solar inverter controller."""
import logging
import os
import sched
import signal
import sys
import time

import influxdbhandler
import inverter_configurator
import voltronic_protocol

def info_loop():
    log.debug('---> INFO loop started --->')
    proto.get_warning_status()
    db.write_measurements(proto.warning, 'warning_status')
    proto.get_device_mode()
    db.write_measurements({'mode': proto.device_mode.name}, 'device_mode')
    proto.get_operational_status()
    db.write_measurements(proto.status, 'operational_status')
    scheduler.enter(5,3,info_loop)
    log.debug('<--- INFO loop finished.')

def setup_loop():
    log.debug('---> SETUP loop started --->')
    icfg._check_inverter_configuration()
    scheduler.enter(30,1,setup_loop)
    log.debug('<--- SETUP loop finished.')

def signal_handler(sig, frame):
    log.info('SIGINT received, exiting.')
    sys.exit(0)

### main program
# logger startup
log = logging.getLogger()
log.setLevel(logging.getLevelName(os.getenv('LOG_LEVEL', 'INFO').upper()))
log_formatter = logging.Formatter('%(asctime)s %(levelname)8s (%(name)s) %(message)s')
log_handler = logging.StreamHandler()
log_handler.setFormatter(log_formatter)
log.addHandler(log_handler)
log.info('STARTING Solar Inverter Controller...')

# initializing main modules
proto = voltronic_protocol.Voltronic()
icfg = inverter_configurator.InverterConfig(proto)
db = influxdbhandler.InfluxDBHandler()

# main loop
signal.signal(signal.SIGINT, signal_handler)
scheduler = sched.scheduler()
setup_loop()
info_loop()
scheduler.run()
