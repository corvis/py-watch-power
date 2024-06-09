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
import hid

from py_watch_power.core import protocol
from py_watch_power.core.dto import (
    DeviceRatingInformationRaw,
    DiscoveredDevice,
    InverterMode,
    InverterStatus,
    InverterStatusRaw,
)
from py_watch_power.core.protocol import Command
from py_watch_power.core.utils import LogMixin


class Inverter:
    """Inverter class to interact with the inverter."""

    def __init__(self, hid_device_path: str):
        self._hid_path = hid_device_path

    def get_status_raw(self) -> InverterStatusRaw:
        """Get the inverter status raw data."""
        reply = protocol.query(Command.QPIGS, self._hid_path)
        parts = reply.decode("utf-8").split(" ")
        if len(parts) > 22:
            parts = parts[:22]
        return InverterStatusRaw(*parts)

    def get_status(self) -> InverterStatus:
        """Get the inverter status."""
        return InverterStatus.from_raw(self.get_status_raw())

    def get_device_rating_information_raw(self) -> DeviceRatingInformationRaw:
        """Get the device rating information raw data."""
        reply = protocol.query(Command.QPIRI, self._hid_path)
        return DeviceRatingInformationRaw(*reply.decode("utf-8").split(" "))

    def get_warning_status_raw(self) -> str:
        """Get the inverter warning status raw data."""
        return protocol.query(Command.QPIWS, self._hid_path).decode("utf-8").strip()

    def get_mode(self) -> InverterMode:
        """Get the inverter mode."""
        reply = protocol.query(Command.QMOD, self._hid_path).decode("utf-8")
        return InverterMode(reply)


class InverterFactory(LogMixin):
    """Inverter factory class to create inverter instances."""

    _VID = 0x0665  # Vendor ID
    _PID = 0x5161  # Product ID

    @classmethod
    def discover(cls) -> list[DiscoveredDevice]:
        """Discover all devices available devices."""
        devices = hid.enumerate(cls._VID, cls._PID)
        return [
            DiscoveredDevice(hid_path=d["path"].decode("utf-8"), vendor_id=cls._VID, product_id=cls._PID)
            for d in devices
        ]

    @classmethod
    def get_first_device(cls) -> DiscoveredDevice:
        """Return the first found device."""
        devices = cls.discover()
        if not devices:
            raise RuntimeError("No devices found.")
        return devices[0]

    @classmethod
    def get_first_device_or_none(cls) -> DiscoveredDevice | None:
        """Return the first found device or None if no devices are found."""
        try:
            return cls.get_first_device()
        except RuntimeError:
            return None

    @classmethod
    def create_by_path(cls, device_path: str) -> Inverter:
        """Create an inverter instance by the provided path."""
        return Inverter(device_path)

    @classmethod
    def create_by_path_or_default(cls, hid_path: str | None = None) -> Inverter:
        """Create an inverter instance by the provided path or by the first found device path."""
        if hid_path:
            return cls.create_by_path(hid_path)
        hid_path = cls.get_first_device().hid_path
        return cls.create_by_path(hid_path)
