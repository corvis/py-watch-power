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


class LogMixin:
    """Convenience super-class to have a logger configured with the class name."""

    _log: logging.Logger | None = None

    @property
    def log(self) -> logging.Logger:
        """Return a logger."""
        if self._log is None:
            self._log = logging.getLogger(self.__class__.__module__ + "." + self.__class__.__name__)
        return self._log


def crc16_xmodem(data: bytes):
    """Generate checksum using CRC-16-CCITT (XModem) Algorithm."""
    data = bytearray(data)
    poly = 0x1021
    crc = 0x0000
    for b in data:
        crc ^= b << 8
        for _ in range(0, 8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ poly) & 0xFFFF
            else:
                crc <<= 1
    return crc & 0xFFFF


def bitstr_to_booleans(bitstr: str) -> list[bool]:
    """Convert a bitstring to a list of booleans. Example: 101011 -> [true, false, true, false, true, true]."""
    return [bit == "1" for bit in bitstr]


def parse_float(value: str) -> float:
    """Parse a float from a string."""
    return float(value) if value else 0.0


def parse_float_or_none(value: str) -> float | None:
    """Parse a float from a string. If input consists of dashes e.g. `---.--` return None."""
    return parse_float(value) if "-" in value[1:] else None


def parse_int(value: str) -> int:
    """Parse an integer from a string."""
    return int(value) if value else 0


def parse_int_or_none(value: str) -> int | None:
    """Parse an integer from a string. If input consists of dashes e.g. `---` return None."""
    return parse_int(value) if "-" in value[1:] else None
