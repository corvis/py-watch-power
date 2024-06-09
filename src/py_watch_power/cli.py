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
import argparse
from inspect import isabstract
import sys

from cli_rack import CLI
from cli_rack.modular import CliAppManager, CliExtension

from py_watch_power import __version__


class VersionCliExtension(CliExtension):
    COMMAND_NAME = "version"
    COMMAND_DESCRIPTION = "Prints application version"

    @classmethod
    def setup_parser(cls, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--short",
            "-s",
            dest="short",
            action="store_true",
            default=False,
            required=False,
            help="Print short version",
        )

    def handle(self, args: argparse.Namespace):
        if args.short:
            CLI.print_info(f"{__version__.VERSION}")
        else:
            CLI.print_info(f"Version: {__version__.VERSION}")
            # CLI.print_info(f"Build: {__version__.BUILD_NUMBER}")
            # CLI.print_info(f"Build Date: {__version__.BUILD_DATE}")
            # CLI.print_info(f"VCS ID: {__version__.VCS_ID}")


def main(argv: list[str]):
    CLI.setup()
    app_manager = CliAppManager(
        "py-watch-power",
        description="CLI tool for inverter monitoring and configuration.",
        epilog=f"Py Watch Power works with a number of inverters distributed as the follwing brands: "
        f"Voltronic, Axpert, Axioma, Mppsolar PIP, Voltacon, Effekta and many others. \n"
        f"\nVersion {__version__.VERSION}",
    )
    app_manager.parse_and_handle_global()
    app_manager.register_extension(VersionCliExtension)

    extensions = app_manager.discovery_manager.discover_cli_extensions("py_watch_power")
    for e in extensions:
        if not isabstract(e.cli_extension):
            app_manager.register_extension(e.cli_extension)

    app_manager.setup()

    try:
        # Parse arguments
        parsed_commands = app_manager.parse(argv)
        if len(parsed_commands) == 1 and parsed_commands[0].cmd is None:
            app_manager.args_parser.print_help()
            CLI.fail("At least one command is required", 7)
        # Run
        exec_manager = app_manager.create_execution_manager()
        exec_manager.run(parsed_commands)
    except Exception as e:
        CLI.print_error(e)


def entrypoint():
    main(sys.argv[1:])
