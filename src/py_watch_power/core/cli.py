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
import abc
import argparse
from dataclasses import asdict
import json

from cli_rack import CLI
from cli_rack.modular import CliExtension

from py_watch_power.core.dto import InverterStatusFlags
from py_watch_power.core.inverter import Inverter, InverterFactory


class BaseInverterCommandExt(CliExtension, metaclass=abc.ABCMeta):
    @classmethod
    def setup_parser(cls, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--dev", "-d", dest="device", required=False, help="Path to the raw HID device e.g. /dev/hidraw0"
        )

    def get_invertor(self, args: argparse.Namespace) -> Inverter:
        device_path = args.device
        inverter = InverterFactory.create_by_path_or_default(device_path)
        # TODO: Check connection here
        return inverter


class DiscoverInverters(BaseInverterCommandExt):
    COMMAND_NAME = "discover"
    COMMAND_DESCRIPTION = "Discover connected inverters."

    @classmethod
    def setup_parser(cls, parser: argparse.ArgumentParser):
        super().setup_parser(parser)
        parser.add_argument(
            "--short",
            "-s",
            dest="short",
            action="store_true",
            required=False,
            help="Return only device path without additional information.",
        )

    def handle(self, args: argparse.Namespace):
        inverters = InverterFactory.discover()
        if not args.short:
            CLI.print_info("Discovered inverters:")
        if not inverters:
            CLI.print_info("No inverters found.")
            return
        for i, inverter in enumerate(inverters):
            if args.short:
                CLI.print_data(inverter.hid_path)
            else:
                CLI.print_data(f"{i + 1}. {inverter.hid_path}" + " - DEFAULT" if i == 0 else "")


class GetModeCommand(BaseInverterCommandExt):
    COMMAND_NAME = "get-mode"
    COMMAND_DESCRIPTION = "Get current inverter mode."

    @classmethod
    def setup_parser(cls, parser: argparse.ArgumentParser):
        super().setup_parser(parser)
        parser.add_argument(
            "--short",
            "-s",
            dest="short",
            action="store_true",
            required=False,
            help="Return 1 letter code instead of the full name.",
        )

    def handle(self, args: argparse.Namespace):
        inverter = self.get_invertor(args)
        mode = inverter.get_mode()
        if args.short:
            print(mode.to_code())
        else:
            print(mode.to_code_with_verbose_name())


class GetStatusCommand(BaseInverterCommandExt):
    COMMAND_NAME = "get-status"
    COMMAND_DESCRIPTION = "Get current inverter status."

    @classmethod
    def setup_parser(cls, parser: argparse.ArgumentParser):
        super().setup_parser(parser)
        parser.add_argument(
            "--json", "-j", dest="json", action="store_true", required=False, help="Return result as JSON"
        )

    def __get_state(self, flags: InverterStatusFlags) -> str:
        state = "Unknown"
        if not flags.charging and flags.load_is_on:
            return "Powering load from battery"
        if flags.charging_ac:
            if flags.load_is_on:
                return "Charging from AC, powering load through BYPASS"
            return "Charging from AC, no load connected"
        if flags.charging_scc:
            if flags.load_is_on:
                return "Charging from SCC, powering load"
            return "Charging from SCC, no load connected"
        return state

    def __fmt_val(self, val: int | float | None, unit: str) -> str:
        return f"{val}{unit}" if val else "N/A"

    def handle(self, args: argparse.Namespace):
        inverter = self.get_invertor(args)
        status = inverter.get_status()
        if args.json:
            CLI.print_data(json.dumps(asdict(status)))
            return
        current_state = self.__get_state(status.status_flags)
        heat_sink_temp = status.inverter_heat_sink_temperature / 10 if status.inverter_heat_sink_temperature else None
        CLI.print_data(f"Inverter status: {current_state}\n")
        CLI.print_data("====== VOLTAGE ======")
        CLI.print_data(f"Grid voltage       : {status.grid_voltage}V")
        CLI.print_data(f"AC output voltage  : {status.grid_voltage}V")
        CLI.print_data("====== BATTERY ======")
        CLI.print_data(f"Battery status             : {status.battery_capacity}%")
        CLI.print_data(f"Battery voltage            : {self.__fmt_val(status.battery_voltage, 'V')}")
        CLI.print_data(f"Battery charge current     : {self.__fmt_val(status.battery_charge_current, 'A')}")
        CLI.print_data(f"Battery discharge current  : {self.__fmt_val(status.battery_discharge_current, 'A')}")
        CLI.print_data("====== MISC ======")
        CLI.print_data(f"Temperature on heat sink   : {self.__fmt_val(heat_sink_temp, 'C')}")

        print(status)
