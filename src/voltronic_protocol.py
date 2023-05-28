"""Voltronic protocol handler module."""
import logging
import os
import time
from enum import Enum

import serial_communicator


class Voltronic(object):
    """Handler class for Voltronic protocol."""

    log = logging.getLogger(__name__)

    @staticmethod
    def _send_cmd(cmd):
        ser = serial_communicator.SerCom()
        response = None
        while True:
            if ser.status in ["OK", "CRC_ERROR", "RESPONSE_TIMEOUT"]:
                Voltronic.log.debug('-> %s ...', cmd)
                ser.send_cmd(cmd)
                response = ser.read_resp()
                if response:
                    if response == 'NAK':
                        Voltronic.log.debug(
                            '%s, serial communication failure: got NAK, repeating...', cmd)
                    else:
                        break
            else:
                time.sleep(1)
            Voltronic.log.debug(
                '%s, serial communication failure: timeout, status: %s, retrying...',
                cmd,
                ser.status)
        Voltronic.log.debug('%s <- %s', cmd, response)
        return response

    class DeviceMode(Enum):
        """Enum definition for DeviceMode."""

        PowerOn = 0
        StandBy = 1
        Line = 2
        Battery = 3
        Fault = 4
        PowerSave = 5

    class BatteryType(Enum):
        """Enum definition for BatteryType."""

        AGM = 0
        Flooded = 1
        User = 2

    class OutputQuality(Enum):
        """Enum definition for OutputQuality."""

        Appliance = 0
        UPS = 1

    class InverterSource(Enum):
        """Enum definition for InverterSource."""

        UtilityFirst = 0
        SolarFirst = 1
        SolarBatteryUtility = 2

    class ChargerSource(Enum):
        """Enum definition for ChargerSource."""

        UtilityFirst = 0
        SolarFirst = 1
        SolarAndUtility = 2
        OnlySolar = 3

    def __init__(self):
        """Constructor."""
        self.protocol_id = None
        self.serial_number = None
        self.firmware_version = None
        self.firmware2_version = None
        self.rating = dict()
        self.default = dict()
        self.status = dict()
        self.flag = dict()
        self.warning = dict()
        self.fault = dict()
        self.device_mode = None

        # self.get_protocol_version()
        # self.get_device_serial()
        # self.get_firmware_version()
        # self.get_firmware2_version()

    def get_protocol_version(self):
        """Protocol ID. PI30 for HS series."""
        self.protocol_id = self._send_cmd('QPI')

    def get_device_serial(self):
        """Device serial number."""
        self.serial_number = self._send_cmd('QID')

    def get_firmware_version(self):
        """Main CPU FW version."""
        self.firmware_version = self._send_cmd('QVFW')

    def get_firmware2_version(self):
        """Another CPU (Solar Charge Controller) FW version."""
        self.firmware2_version = self._send_cmd('QVFW2')

    def get_device_rating(self):
        """Device Rating Information inquiry."""
        response = self._send_cmd('QPIRI').split()
        self.rating['grid_voltage'] = float(response[0])
        self.rating['grid_current'] = float(response[1])
        self.rating['ac_output_voltage'] = float(response[2])
        self.rating['ac_output_frequency'] = float(response[3])
        self.rating['ac_output_current'] = float(response[4])
        self.rating['ac_output_apparent_power'] = int(response[5])
        self.rating['ac_output_active_power'] = int(response[6])
        self.rating['battery_nominal_voltage'] = float(response[7])
        self.rating['battery_recharge_voltage'] = float(response[8])
        self.rating['battery_under_voltage'] = float(response[9])
        self.rating['battery_bulk_voltage'] = float(response[10])
        self.rating['battery_float_voltage'] = float(response[11])
        self.rating['battery_type'] = {
            '0': Voltronic.BatteryType.AGM,
            '1': Voltronic.BatteryType.Flooded,
            '2': Voltronic.BatteryType.User
        }[response[12]]
        self.rating['max_ac_charging_current'] = int(response[13])
        self.rating['max_charging_current'] = int(response[14])
        self.rating['output_quality'] = {
            '0': Voltronic.OutputQuality.Appliance,
            '1': Voltronic.OutputQuality.UPS
        }[response[15]]
        self.rating['output_source_priority'] = {
            '0': Voltronic.InverterSource.UtilityFirst,
            '1': Voltronic.InverterSource.SolarFirst,
            '2': Voltronic.InverterSource.SolarBatteryUtility
        }[response[16]]
        self.rating['charger_source_priority'] = {
            '0': Voltronic.ChargerSource.UtilityFirst,
            '1': Voltronic.ChargerSource.SolarFirst,
            '2': Voltronic.ChargerSource.SolarAndUtility,
            '3': Voltronic.ChargerSource.OnlySolar
        }[response[17]]
        self.rating['parallel_max_num'] = int(response[18])
        self.rating['machine_type'] = int(response[19])
        self.rating['topology'] = int(response[20])
        self.rating['output_mode'] = int(response[21])
        self.rating['battery_redischarge_voltage'] = float(response[22])
        self.rating['pv_ok_condition'] = int(response[23])
        self.rating['pv_power_balance'] = int(response[24])
        self.log.debug("Current rating: %s", self.rating)

    def get_options(self):
        """Device options statuses (enable/disable)."""
        response = self._send_cmd('QFLAG').split('D')
        self.flag['buzzer'] = 'a' not in response[1]
        self.flag['overload_bypass'] = 'b' not in response[1]
        self.flag['power_saving'] = 'j' not in response[1]
        self.flag['lcd_escape_timeout'] = 'k' not in response[1]
        self.flag['overload_restart'] = 'u' not in response[1]
        self.flag['overtemperature_restart'] = 'v' not in response[1]
        self.flag['lcd_backlight'] = 'x' not in response[1]
        self.flag['primary_source_interrupt_alarm'] = 'y' not in response[1]
        self.flag['fault_code_record'] = 'z' not in response[1]
        self.log.debug("Current device options: %s", self.flag)

    def get_operational_status(self):
        """Device general status parameters inquiry."""
        response = self._send_cmd('QPIGS').split()
        self.status['grid_voltage'] = float(response[0])
        self.status['grid_frequency'] = float(response[1])
        self.status['ac_output_voltage'] = float(response[2])
        self.status['ac_output_frequency'] = float(response[3])
        self.status['ac_output_apparent_power'] = int(response[4])
        self.status['ac_output_active_power'] = int(response[5])
        self.status['output_load_percent'] = int(response[6])
        self.status['bus_voltage'] = int(response[7])
        self.status['battery_voltage'] = float(response[8])
        self.status['battery_charging_current'] = int(response[9])
        self.status['battery_capacity'] = int(response[10])
        self.status['heat_sink_temperature'] = int(response[11])
        self.status['pv_input_current'] = int(response[12])
        self.status['pv_input_voltage'] = float(response[13])
        self.status['scc_battery_voltage'] = float(response[14])
        self.status['battery_discharge_current'] = int(response[15])
        device_status_bits = int(response[16], 2)
        self.status['ac_charging_status'] = bool(device_status_bits & 0x01)
        self.status['solar_charging_status'] = bool(device_status_bits & 0x02)
        self.status['charging_status'] = bool(device_status_bits & 0x04)
        self.status['constant_voltage_charging_phase'] = \
            bool(device_status_bits & 0x08)
        self.status['load_status'] = bool(device_status_bits & 0x10)
        self.status['scc_firmware_updated'] = bool(device_status_bits & 0x20)
        self.status['configuration_changed'] = bool(device_status_bits & 0x40)
        self.status['sbu_priority_version'] = bool(device_status_bits & 0x80)
        self.log.debug("Current status: %s", self.status)

    def get_device_mode(self):
        """Device Mode inquiry."""
        response = self._send_cmd('QMOD')
        self.device_mode = {
            'P': Voltronic.DeviceMode.PowerOn,
            'S': Voltronic.DeviceMode.StandBy,
            'L': Voltronic.DeviceMode.Line,
            'B': Voltronic.DeviceMode.Battery,
            'F': Voltronic.DeviceMode.Fault,
            'H': Voltronic.DeviceMode.PowerSave
        }[response]
        self.log.debug("Current device mode: %s", self.device_mode)

    def get_warning_status(self):
        """Device Warning Status inquiry."""
        device_warning_bits = int(self._send_cmd('QPIWS'), 2)
        self.warning['battery_too_low_to_charge'] = \
            bool(device_warning_bits & 0x04)
        self.warning['mppt_overload_warning'] = \
            bool(device_warning_bits & 0x08)
        self.warning['mppt_overload_fault'] = bool(device_warning_bits & 0x10)
        self.warning['pv_voltage_high'] = bool(device_warning_bits & 0x20)
        self.warning['power_limit'] = bool(device_warning_bits & 0x40)
        self.fault['battery_short'] = bool(device_warning_bits & 0x80)
        self.fault['current_sensor_fail'] = bool(device_warning_bits & 0x100)
        self.fault['battery_open'] = bool(device_warning_bits & 0x200)
        self.fault['op_dc_overvoltage'] = bool(device_warning_bits & 0x400)
        self.fault['self_test_fail'] = bool(device_warning_bits & 0x800)
        self.fault['inverter_soft_fail'] = bool(device_warning_bits & 0x1000)
        self.fault['inverter_overcurrent'] = bool(device_warning_bits & 0x2000)
        self.fault['eeprom_fault'] = bool(device_warning_bits & 0x4000)
        self.warning['overload'] = bool(device_warning_bits & 0x8000)
        self.warning['battery_under_shutdown'] = \
            bool(device_warning_bits & 0x20000)
        self.warning['battery_low'] = bool(device_warning_bits & 0x800000)
        self.warning['battery_high'] = bool(device_warning_bits & 0x1000000)
        self.warning['fan_locked'] = bool(device_warning_bits & 0x2000000)
        self.warning['overtemperature'] = bool(device_warning_bits & 0x4000000)
        self.fault['inverter_voltage_too_high'] = \
            bool(device_warning_bits & 0x8000000)
        self.fault['inverter_voltage_too_low'] = \
            bool(device_warning_bits & 0x10000000)
        self.warning['opv_short'] = bool(device_warning_bits & 0x20000000)
        self.warning['line_fail'] = bool(device_warning_bits & 0x40000000)
        self.fault['bus_soft_fail'] = bool(device_warning_bits & 0x80000000)
        self.fault['bus_undervoltage'] = \
            bool(device_warning_bits & 0x100000000)
        self.fault['bus_overvoltage'] = bool(device_warning_bits & 0x200000000)
        self.fault['inverter_fault'] = bool(device_warning_bits & 0x400000000)
        self.log.debug("Current warnings: %s %s", self.warning, self.fault)

    def get_defaults(self):
        """The default setting value information."""
        defaults = self._send_cmd('QDI').split()
        self.default['ac_output_voltage'] = float(defaults[0])
        self.default['ac_output_frequency'] = float(defaults[1])

    def get_charging_current_values(self):
        """Enquiry selectable value about max charging current."""
        self._send_cmd('QMCHGCR')

    def get_utility_charging_current_values(self):
        """Enquiry selectable value about max utility charging current."""
        self._send_cmd('QMUCHGCR')

    def get_dsp_has_bootstrap(self):
        """Enquiry DSP has bootstrap or not."""
        self._send_cmd('QBOOT')

    def get_parallel_output_mode(self):
        """Enquiry output mode (for 4K/5K)."""
        self._send_cmd('QOPM')

    def get_parallel_operational_status(self, unit_number):
        """Parallel Information inquiry (for 4K/5K)."""
        self._send_cmd('QPGS' + str(unit_number))

    def set_inverter_source(self, inverter_source: InverterSource):
        """POP <NN> <cr>: Setting device output source priority."""
        self._send_cmd('POP' + str(inverter_source.value).zfill(2))

    def set_battery_type(self, battery_type: BatteryType):
        """PBT <NN> <cr>: Setting battery type."""
        self._send_cmd('PBT' + str(battery_type.value).zfill(2))
    def set_battery_bulk_voltage(self, bulk_voltage: float):
        """PCVV <nn.n> <cr>: Set battery bulk charge C.V. voltage."""
        self._send_cmd('PCVV' + '{:04.1f}'.format(bulk_voltage))
    def set_battery_float_voltage(self, float_voltage: float):
        """PBFT <nn.n> <cr>: Set battery float charge C.C. voltage."""
        self._send_cmd('PBFT' + '{:04.1f}'.format(float_voltage))
    def set_battery_redischarge_voltage(self, redischarge_voltage: float):
        """PBDV <nn.n> <cr>: Set battery redischarge voltage."""
        self._send_cmd('PBDV' + '{:04.1f}'.format(redischarge_voltage))
    def set_battery_recharge_voltage(self, recharge_voltage: float):
        """PBCV <nn.n> <cr>: Set battery recharge voltage."""
        self._send_cmd('PBCV' + '{:04.1f}'.format(recharge_voltage))
    def set_battery_cutoff_voltage(self, cutoff_voltage: float):
        """PSDV <nn.n> <cr>: Set battery cutoff voltage."""
        self._send_cmd('PSDV' + '{:04.1f}'.format(cutoff_voltage))

    def set_charger_source(self, charger_source: ChargerSource):
        """PCP <NN> <cr>: Setting device charger priority."""
        self._send_cmd('PCP' + str(charger_source.value).zfill(2))

    def set_output_quality(self, output_quality: OutputQuality):
        """PGR <NN> <cr>: Setting device grid working range."""
        self._send_cmd('PGR' + str(output_quality.value).zfill(2))

    def set_max_charging_current(self, max_current: int):
        """MCHGC <mnn> <cr>: Setting max charging current."""
        self._send_cmd('MCHGC' + str(max_current).zfill(3))

    def set_max_utility_charging_current(self, max_current: int):
        """MUCHGC <mnn> <cr>: Setting utility max charging current."""
        self._send_cmd('MUCHGC' + str(max_current).zfill(3))

    def _set_flag_option(self, flag, enable):
        """PE <XXX> / PD <XXX> <CRC> <cr>: setting some status enable/disable"""
        if enable:
            self._send_cmd('PE' + flag)
        else:
            self._send_cmd('PD' + flag)

    def set_flag_b(self, flag, enable):
        self._set_flag_option('b', enable)

    def set_flag_u(self, flag, enable):
        self._set_flag_option('u', enable)

    def set_flag_v(self, flag, enable):
        self._set_flag_option('v', enable)

    def set_flag_y(self, flag, enable):
        self._set_flag_option('y', enable)

    # PF < cr >: Setting control parameter to default value
    # F < nn > < cr >: Setting device output rating frequency
    # PSDV < nn.n > <cr>: Setting battery cutoff voltage(Battery under voltage)
    # PCVV < nn.n > <cr>: Setting battery constant voltage charging voltage
    # PBFT < nn.n > <cr>: Setting battery float charging voltage
    # PPVOKC < n > <cr>: Setting PV OK condition
    # PSPB < n > <cr>: Setting solar power balance
    # POPM <mn> <cr>: Set output mode (for 4000/5000)
    # PPCP <MNN> <cr>: Setting parallel device charger priority (for 4000/5000)
