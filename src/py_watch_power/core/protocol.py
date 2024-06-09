#
# Py Watch Power - Client software for managing inverters and solar stations.
# Copyright (C) {{ year }}  Dmitry Berezovsky
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import logging

import hid

from py_watch_power.core.utils import crc16_xmodem

LOGGER = logging.getLogger("protocol")


class CommunicationError(RuntimeError):
    """Exception raised when there is a communication error with the device."""

    def __init__(
        self, msg: str, hid_device_path: str | None = None, command: bytes | None = None, reply: bytes | None = None
    ) -> None:
        super().__init__(msg)
        self.hid_device_path = hid_device_path
        self.command = command
        self.reply = reply
        self.msg = msg

    def __str__(self) -> str:
        res = super().__str__()
        if self.command:
            res += f" Raw command: {repr(self.command)}"
        if self.reply:
            res += f" Raw Reply: {repr(self.reply)}"
        return res


def _prepare_command(raw_command: bytes) -> bytes:
    """
    Prepare a command to be sent to the device.

    This function takes a raw command, calculates its CRC16-XMODEM checksum,
    appends the checksum to the command, and finally appends a carriage return
    character ('0x0d') to the end of the command.

    :param raw_command: raw command to be prepared.
    :return bytes: prepared command ready to be sent to the device.
    """
    return raw_command + crc16_xmodem(raw_command).to_bytes(2, "big") + b"\x0d"


def _send(prepared_command: bytes, hid_device_path: str) -> bytes:
    read_len = 100
    try:
        with hid.Device(path=hid_device_path.encode("utf-8")) as h:
            LOGGER.debug("Sending command to %s: %s", hid_device_path, prepared_command)
            h.write(prepared_command)
            # Read from the device
            result = h.read(read_len, timeout=2000)
            while chunk := h.read(read_len, timeout=100):
                result += chunk
            # Check if we got any data
            if not result:
                raise CommunicationError("Didn't get any reply from the devices withing timeout interval.")
            # PARSE REPLY
            # Every reply has the following structure:
            #    (<reply-bytes><crc16>\r
            LOGGER.debug("Got reply: %s", result)
            # First byte of the reply should be always 0x28 which is a `(` symbol
            if result[0] != 0x28:
                raise CommunicationError("Invalid start byte", reply=result)
            # Every command ends with 0x0d which is `\r`, but there are might be some trailing zeros,
            # so we need to find the last \r bytes in the object
            for i, b in enumerate(reversed(result)):
                if b == 0:
                    continue
                if b == 0x0D:
                    i += 1
                    break
                else:
                    raise CommunicationError("Invalid stop byte", reply=result)
            if i >= len(result) - 1:
                raise CommunicationError("Invalid stop byte", reply=result)
            # Separate data from CRC
            data_with_crc = result[1:-i]
            data, crc_from_reply = data_with_crc[:-2], int.from_bytes(data_with_crc[-2:], "big")
            # Check CRC
            actual_crc = crc16_xmodem(b"(" + data)
            if actual_crc != crc_from_reply:
                raise CommunicationError(
                    f"Invalid CRC. Actual: {actual_crc}, From Response: {crc_from_reply}", reply=result
                )
            LOGGER.debug("Command was successful. Reply from device: %s", data)
            return data
    except Exception as e:
        if isinstance(e, CommunicationError):
            e.hid_device_path = hid_device_path
            e.command = prepared_command
            raise e
        else:
            raise CommunicationError(str(e), hid_device_path=hid_device_path, command=prepared_command) from e


def query(command: bytes, hid_device_path: str) -> bytes:
    """
    Send a query to the device and return the reply.

    :param command: command to be sent to the device.
    :param hid_device_path: path to the device.
    """
    if command[0] != 0x51:
        LOGGER.warning("Invalid command `%s`. Command should start with `Q` (0x51)", command)
    prepared_cmd = _prepare_command(command)
    return _send(prepared_cmd, hid_device_path)


class Command:
    """List of all available commands that can be sent to the inverter."""

    QMOD = b"QMOD"
    QPIGS = b"QPIGS"
    QPIRI = b"QPIRI"
    QPIWS = b"QPIWS"
