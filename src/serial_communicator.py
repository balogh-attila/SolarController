"""Serial communication handler module."""
import os
import struct
import serial

from PyCRC.CRCCCITT import CRCCCITT


class SerCom(object):
    """Class for serial communication handling."""

    SERIAL_PORT_NAME =  os.getenv('SERIAL_PORT', '/dev/ttyUSB0')
    CR = b'\x0d'

    def __init__(self):
        """Initialize serial line."""
        self._ser = serial.Serial()
        self._ser.port = SerCom.SERIAL_PORT_NAME
        self._ser.baudrate = 2400
        self._ser.timeout = 3
        try:
            self._ser.open()
        except serial.SerialException:
            # log serial error
            self.status = "ERROR"
            return
        self.status = "OK"
        # log(ser.name)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Gracefully closes serial connection on exit."""
        self._ser.close()

    @staticmethod
    def _get_crc(raw_data) -> bytes:
        if raw_data == "POP02":
            # workaround of axpert firmware bug
            return struct.pack('>H', 0xE20B)
        else:
            return struct.pack('>H', CRCCCITT().calculate(raw_data))

    def _decode_response(self, data_with_crc: bytearray) -> str:
        response_crc = bytes(data_with_crc[-2:])
        response_data = bytes(data_with_crc[:-2])
        if response_crc == SerCom._get_crc(response_data):
            self.response_is_valid = True
            self.response_status = "CRC_OK"
        else:
            self.response_is_valid = False
            self.response_status = "CRC_ERROR"
        return response_data.decode(encoding='ascii')

    def send_cmd(self, raw_cmd: str):
        """Send serial command with CRC."""
        self.status = "SENDING"
        cmd = bytearray(raw_cmd, encoding='ascii')
        cmd.extend(SerCom._get_crc(raw_cmd))
        cmd.extend(SerCom.CR)
        self._ser.write(cmd)

    def read_resp(self) -> str:
        """Receive serial response with CRC check."""
        self.status = "RECEIVING"
        raw_response = bytearray()
        while True:
            response_byte = self._ser.read()
            if len(response_byte) == 0:
                self.status = "RESPONSE_TIMEOUT"
                return False
            if response_byte == SerCom.CR:
                break
            raw_response.extend(response_byte)
        response_str = self._decode_response(raw_response)
        if self.response_is_valid:
            self.status = "OK"
            return response_str[1:]
        self.status = self.response_status
        return False
