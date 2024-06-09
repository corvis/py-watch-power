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
from dataclasses import dataclass
from enum import Enum

from py_watch_power.core.utils import bitstr_to_booleans, parse_float, parse_float_or_none, parse_int, parse_int_or_none


@dataclass
class DiscoveredDevice:
    """Discovered device data."""

    hid_path: str
    vendor_id: int
    product_id: int
    serial_number: str | None = None


class InverterMode(Enum):
    """Inverter mode enumeration."""

    POWER_ON = "P"
    STANDBY = "S"
    LINE = "L"
    BATTERY = "B"
    FAULT = "F"
    POWER_SAVING = "H"

    def to_verbose_name(self) -> str:
        """Return a verbose string representation of the mode."""
        return {
            InverterMode.POWER_ON: "Power on",
            InverterMode.STANDBY: "Standby",
            InverterMode.LINE: "Line",
            InverterMode.BATTERY: "Battery",
            InverterMode.FAULT: "Fault",
            InverterMode.POWER_SAVING: "Power saving",
        }[self]

    def to_code(self) -> str:
        """Return a 1-letter code representation of the mode."""
        return self.value

    def to_code_with_verbose_name(self) -> str:
        """Return a 1-letter code representation of the mode."""
        return f"{self.value} ({self.to_verbose_name()})"


class BatteryType(Enum):
    """Battery type enumeration."""

    AGM = "0"
    Flooded = "1"
    USER = "2"


@dataclass
class InverterStatusRaw:
    """Inverter status raw data."""

    grid_voltage: str
    grid_frequency: str
    ac_output_voltage: str
    ac_output_frequency: str
    ac_output_apparent_power: str
    ac_output_active_power: str
    output_load_percent: str
    bus_voltage: str
    battery_voltage: str
    battery_charge_current: str
    battery_capacity: str
    inverter_heat_sink_temperature: str
    pv_input_current_for_battery: str
    pv_input_voltage: str
    battery_voltage_from_scc: str
    battery_discharge_current: str
    device_status: str
    # Properties below were added in newer versions
    battery_voltage_offset_for_fans_on: str | None = None
    eeprom_version: str | None = None
    pv_charging_power: str | None = None
    device_status_2: str | None = None


@dataclass
class InverterStatusFlags:
    """Inverter status flags."""

    add_sbu_priority_version: bool
    configuration_changed: bool
    scc_firmware_updated: bool
    load_is_on: bool
    battery_voltage_to_steady_while_charging: bool
    charging: bool
    charging_scc: bool
    charging_ac: bool
    charging_to_floating: bool | None = None
    switch_on: bool | None = None

    @classmethod
    def from_bit_str(cls, bitstr: str) -> "InverterStatusFlags":
        """Create an InverterStatusFlags instance from a bit string."""
        return cls(*bitstr_to_booleans(bitstr))


@dataclass
class InverterStatus:
    """Inverter status data."""

    grid_voltage: float
    """Grid voltage in volts."""
    grid_frequency: float
    """Grid frequency in Hz."""
    ac_output_voltage: float
    """AC output voltage in volts."""
    ac_output_frequency: float
    """AC output frequency in Hz."""
    ac_output_apparent_power: int
    """AC output apparent power in VA."""
    ac_output_active_power: int
    """AC output active power in W."""
    output_load_percent: int
    """Output load percent. 0-100%."""
    bus_voltage: int
    """Bus voltage in volts."""
    battery_voltage: float | None
    """Battery voltage in volts."""
    battery_charge_current: int | None
    """Battery charge current in amperes."""
    battery_capacity: int
    """Current battery charge status in percent. 100% means fully charged."""
    inverter_heat_sink_temperature: int
    """Inverter heat sink temperature in Celsius."""
    pv_input_current_for_battery: int | None
    """PV input current for battery in amperes."""
    pv_input_voltage: float | None
    """PV input voltage in volts."""
    battery_voltage_from_scc: float | None
    """Battery voltage from SCC in volts."""
    battery_discharge_current: int | None
    """Battery discharge current in amperes."""
    status_flags: InverterStatusFlags
    # Properties below were added in newer versions
    battery_voltage_offset_for_fans_on: int | None = None
    """Battery voltage offset for fans on in mV."""
    eeprom_version: int | None = None
    """EEPROM version."""
    pv_charging_power: int | None = None
    """PV charging power in watts."""

    @classmethod
    def from_raw(cls, raw: InverterStatusRaw):
        """Create an InverterStatus instance from raw data."""
        result = cls(
            grid_voltage=parse_float(raw.grid_voltage),
            grid_frequency=parse_float(raw.grid_frequency),
            ac_output_voltage=parse_float(raw.ac_output_voltage),
            ac_output_frequency=parse_float(raw.ac_output_frequency),
            ac_output_apparent_power=parse_int(raw.ac_output_apparent_power),
            ac_output_active_power=parse_int(raw.ac_output_active_power),
            output_load_percent=parse_int(raw.output_load_percent),
            bus_voltage=parse_int(raw.bus_voltage),
            battery_voltage=parse_float_or_none(raw.battery_voltage),
            battery_charge_current=parse_int_or_none(raw.battery_charge_current),
            battery_capacity=parse_int(raw.battery_capacity),
            inverter_heat_sink_temperature=parse_int(raw.inverter_heat_sink_temperature),
            pv_input_current_for_battery=parse_int_or_none(raw.pv_input_current_for_battery),
            pv_input_voltage=parse_float_or_none(raw.pv_input_voltage),
            battery_voltage_from_scc=parse_float_or_none(raw.battery_voltage_from_scc),
            battery_discharge_current=parse_int_or_none(raw.battery_discharge_current),
            status_flags=InverterStatusFlags.from_bit_str(raw.device_status),
            battery_voltage_offset_for_fans_on=parse_int(raw.battery_voltage_offset_for_fans_on)
            if raw.battery_voltage_offset_for_fans_on
            else None,
            eeprom_version=parse_int(raw.eeprom_version) if raw.eeprom_version else None,
            pv_charging_power=parse_int(raw.pv_charging_power) if raw.pv_charging_power else None,
        )
        if raw.device_status_2:
            result.status_flags.charging_to_floating = raw.device_status_2[0] == "1"
            result.status_flags.switch_on = raw.device_status_2[1] == "1"
        return result


@dataclass
class DeviceRatingInformationRaw:
    """Device rating information raw data."""

    grid_rating_voltage: str
    grid_rating_current: str
    ac_output_rating_voltage: str
    ac_output_rating_frequency: str
    ac_output_rating_current: str
    ac_output_rating_apparent_power: str
    ac_output_rating_active_power: str
    battery_rating_voltage: str
    battery_recharge_voltage: str
    battery_under_voltage: str
    battery_bulk_voltage: str
    battery_float_voltage: str
    battery_type: str
    current_max_ac_charging_current: str
    current_max_charging_current: str
    input_voltage_range: str
    output_source_priority: str
    charger_source_priority: str
    max_parallel_units: str
    machine_type: str
    topological_structure: str
    output_mode: str
    battery_redischarge_voltage: str
    pv_ok_condition_for_parallel: str
    pv_power_balance: str
