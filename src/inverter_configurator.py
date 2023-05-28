"""InverterConfig class."""
import logging
import os
import yaml

from voltronic_protocol import Voltronic


class InverterConfig(object):
    """Responsible for configuring the inverter based on yaml settings."""

    CONFIG = os.getenv('CONFIG', 'etc/solar/config.yaml')

    icfg = dict()
    log = logging.getLogger(__name__)

    def Icfg(cls):
        return cls.icfg

    def _load_config(self):
        """Create Icfg object property.

        Load, parse and store desired inverter configuration from yaml
        configuration file.
        """

        self.log.debug("Loading configuration...")
        old_cfg = self.icfg.copy()

        with open(self.CONFIG) as yaml_file:
            # load yaml config file
            parsed_cfg = yaml.safe_load(yaml_file)
            # parse battery type
            self.icfg['battery_type'] = {
                'agm': Voltronic.BatteryType.AGM,
                'flooded': Voltronic.BatteryType.Flooded,
                'user': Voltronic.BatteryType.User
            }[parsed_cfg['battery']['type']]
            # parse battery charger voltage limits
            self.icfg['battery_bulk_voltage'] = parsed_cfg['battery']['bulk_voltage']
            self.icfg['battery_float_voltage'] = parsed_cfg['battery']['float_voltage']
            self.icfg['battery_redischarge_voltage'] = parsed_cfg['battery']['redischarge_voltage']
            self.icfg['battery_recharge_voltage'] = parsed_cfg['battery']['recharge_voltage']
            self.icfg['battery_cutoff_voltage'] = parsed_cfg['battery']['cutoff_voltage']
            # parse inverter source
            self.icfg['inverter_source'] = {
                'utility_first': Voltronic.InverterSource.UtilityFirst,
                'solar_first': Voltronic.InverterSource.SolarFirst,
                'SBU': Voltronic.InverterSource.SolarBatteryUtility
            }[parsed_cfg['inverter']['source']]
            # parse inverter options
            self.icfg['inverter_overload_bypass'] = parsed_cfg['inverter']['overload']['bypass']
            self.icfg['inverter_overload_restart'] = parsed_cfg['inverter']['overload']['restart']
            self.icfg['inverter_overtemp_restart'] = parsed_cfg['inverter']['overtemp']['restart']
            self.icfg['inverter_alarm_on_psi'] = parsed_cfg['inverter']['alarm']['primary_source_interrupt']
            self.icfg['inverter_output_quality'] = {
                'appliance': Voltronic.OutputQuality.Appliance,
                'ups': Voltronic.OutputQuality.UPS
            }[parsed_cfg['inverter']['output_quality']]
            # parse charger source
            self.icfg['charger_source'] = {
                'utility_first': Voltronic.ChargerSource.UtilityFirst,
                'solar_first': Voltronic.ChargerSource.SolarFirst,
                'solar_and_utility': Voltronic.ChargerSource.SolarAndUtility,
                'only_solar': Voltronic.ChargerSource.OnlySolar
            }[parsed_cfg['charger']['source']]
            # parse charger currents
            self.icfg['max_charging_current'] = parsed_cfg['charger']['max_current']
            self.icfg['max_ac_charging_current'] = parsed_cfg['charger']['utility_current']

        if self.icfg != old_cfg:
            self.log.info("Configuration loaded from [{}]."
                          .format(self.CONFIG))


    def _check_config_parameter(self, curr_value, cfg_value, cfg_name, func):
        self.log.debug("Check inverter configuration [{}]: {} -> {}."
                       .format(cfg_name, curr_value, cfg_value))
        if curr_value != cfg_value:
            self.log.info("Modify inverter configuration [{}]: {} -> {}."
                          .format(cfg_name, curr_value, cfg_value))
            func(cfg_value)

    def _check_inverter_source(self):
        self._check_config_parameter(
            self.proto.rating['output_source_priority'],
            self.icfg['inverter_source'],
            'inverter source',
            self.proto.set_inverter_source
        )

    def _check_charger_source(self):
        self._check_config_parameter(
            self.proto.rating['charger_source_priority'],
            self.icfg['charger_source'],
            'charger source',
            self.proto.set_charger_source
        )

    def _check_max_charging_current(self):
        self._check_config_parameter(
            self.proto.rating['max_charging_current'],
            self.icfg['max_charging_current'],
            'charging current',
            self.proto.set_max_charging_current
        )

    def _check_max_utility_charging_current(self):
        self._check_config_parameter(
            self.proto.rating['max_ac_charging_current'],
            self.icfg['max_ac_charging_current'],
            'utility charging current',
            self.proto.set_max_utility_charging_current
        )

    def _check_inverter_overload_bypass(self):
        self._check_config_parameter(
            self.proto.flag['overload_bypass'],
            self.icfg['inverter_overload_bypass'],
            'inverter overload bypass',
            self.proto.set_flag_b
        )

    def _check_inverter_overload_restart(self):
        self._check_config_parameter(
            self.proto.flag['overload_restart'],
            self.icfg['inverter_overload_restart'],
            'inverter overload restart',
            self.proto.set_flag_u
        )

    def _check_inverter_overtemp_restart(self):
        self._check_config_parameter(
            self.proto.flag['overtemperature_restart'],
            self.icfg['inverter_overtemp_restart'],
            'inverter overtemperature restart',
            self.proto.set_flag_v
        )

    def _check_inverter_alarm_on_primary_source_interrupt(self):
        self._check_config_parameter(
            self.proto.flag['primary_source_interrupt_alarm'],
            self.icfg['inverter_alarm_on_psi'],
            'alarm on primary source interrupt',
            self.proto.set_flag_y
        )

    def _check_output_quality(self):
        self._check_config_parameter(
            self.proto.rating['output_quality'],
            self.icfg['inverter_output_quality'],
            'output quality',
            self.proto.set_output_quality
        )

    def _check_battery_type(self):
        self._check_config_parameter(
            self.proto.rating['battery_type'],
            self.icfg['battery_type'],
            'battery type',
            self.proto.set_battery_type
        )
    def _check_battery_bulk_voltage(self):
        self._check_config_parameter(
            self.proto.rating['battery_bulk_voltage'],
            self.icfg['battery_bulk_voltage'],
            'battery bulk charge voltage',
            self.proto.set_battery_bulk_voltage
        )
    def _check_battery_float_voltage(self):
        self._check_config_parameter(
            self.proto.rating['battery_float_voltage'],
            self.icfg['battery_float_voltage'],
            'battery float charge voltage',
            self.proto.set_battery_float_voltage
        )
    def _check_battery_redischarge_voltage(self):
        self._check_config_parameter(
            self.proto.rating['battery_redischarge_voltage'],
            self.icfg['battery_redischarge_voltage'],
            'battery redischarge voltage',
            self.proto.set_battery_redischarge_voltage
        )
    def _check_battery_recharge_voltage(self):
        self._check_config_parameter(
            self.proto.rating['battery_recharge_voltage'],
            self.icfg['battery_recharge_voltage'],
            'battery recharge voltage',
            self.proto.set_battery_recharge_voltage
        )
    def _check_battery_cutoff_voltage(self):
        self._check_config_parameter(
            self.proto.rating['battery_under_voltage'],
            self.icfg['battery_cutoff_voltage'],
            'battery cutoff voltage',
            self.proto.set_battery_cutoff_voltage
        )


    def _check_inverter_configuration(self):
        self._load_config()

        self.proto.get_device_rating()
        self.proto.get_options()

        self._check_inverter_source()
        self._check_charger_source()
        self._check_max_utility_charging_current()
        self._check_max_charging_current()
        self._check_inverter_overload_bypass()
        self._check_inverter_overload_restart()
        self._check_inverter_overtemp_restart()
        self._check_inverter_alarm_on_primary_source_interrupt()
        self._check_battery_type()
        self._check_battery_bulk_voltage()
        self._check_battery_float_voltage()
        self._check_battery_redischarge_voltage()
        self._check_battery_recharge_voltage()
        self._check_battery_cutoff_voltage()
        self._check_output_quality()

        self.proto.get_device_rating()
        self.proto.get_options()


    def __init__(self, proto: Voltronic):
        """Initialize inverter configuration."""
        self.proto = proto
