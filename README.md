![Py Watch Power Cover Picture](https://raw.githubusercontent.com/corvis/py-watch-power/master/docs/assets/cover-picture.png "Py Watch Power Cover Picture")

<h2 align="center">Py Watch Power</h2>

<p align="center">
<a href="https://pypi.org/project/pywatchpower/"><img src="https://img.shields.io/pypi/l/pywatchpower?style=for-the-badge" title="License: GPL-3"/></a> 
<a href="https://pypi.org/project/pywatchpower/"><img src="https://img.shields.io/pypi/pyversions/pywatchpower?style=for-the-badge" title="Python Versions"/></a> 
<a href="https://github.com/psf/black/"><img src="https://img.shields.io/badge/Code%20Style-black-black?style=for-the-badge" title="Code style: black"/></a> 
<a href="https://pypi.org/project/pywatchpower/"><img src="https://img.shields.io/pypi/v/pywatchpower?style=for-the-badge" title="PyPy Version"/></a> 
<a href="https://pypi.org/project/pywatchpower/"><img src="https://img.shields.io/pypi/dm/pywatchpower?style=for-the-badge" title="PyPy Downloads"/></a> 
<br>
<a href="https://github.com/corvis/py-watch-power/actions/workflows/sanity-check.yml"><img src="https://img.shields.io/github/workflow/status/corvis/py-watch-power/Sanity%20Check?style=for-the-badge" title="Build Status"/></a> 
<a href="https://github.com/corvis/py-watch-power/"><img src="https://img.shields.io/github/last-commit/corvis/py-watch-power?style=for-the-badge" title="Last Commit"/></a> 
<a href="https://github.com/corvis/py-watch-power/releases/"><img src="https://img.shields.io/github/release-date/corvis/py-watch-power?style=for-the-badge" title="Last Release"/></a> 
</p>

PyWatchPower is an open-source project designed to read data from and control photovoltaic (PV) inverters.
With PyWatchPower, you can monitor the real-time status of your PV system, including battery levels,
voltage, and other critical metrics.

This tool supports various user interfaces, such as MQTT, CLI, JSON REST API and has integration with Home Assistant,
making it versatile and easy to integrate with different systems.
It is compatible with inverters from numerous manufacturers that implement protocols similar to the PIP-4048.

# Supported Inverters

PyWatchPower supports any inverter implementing a protocol similar to the PIP-4048. Unfortunately protocol doesn't have
distinct name and manufacturers doesn't clearly state that they are using it. Also there are a number of white-labeled
devices on the market which are actually the same rebranded device. So if your device looks like one of this and has USB
or serial port, most likely it is supported:

![Py Watch Power Cover Picture](https://raw.githubusercontent.com/corvis/py-watch-power/master/docs/assets/compatible-invertors.png "Supported Devices")

Some of the manufacturers whose devices are compatible:

* Axioma Energy
* MPP PIP-4048
* MPP Solar
* Voltronic
* Voltacon
* Effecta
* Many others

# Features

* Real-time Monitoring: Access current state, battery status, voltage, and more.
* Control: Change mode, set the battery charge current, and more.
* Multiple Interfaces:
    * MQTT: For seamless integration with IoT devices and platforms
    * CLI: Command-line interface for direct interaction and scripting.
    * JSON REST API: For web-based interaction and integration with other applications
* Home Assistant Integration: Works via MQTT, supports automatic entities discovery.
* Docker Support: Run PyWatchPower in a containerized environment.

# Installation

## Install from PyPi

You can use either `pipx` (recommended) or `pip` to install PyWatchPower:

```bash
pipx pywatchpower
```

The following extras are available:

* mqtt - for homeassistant integration just or mqtt support
* rest - for rest api support
* all - for all extras

## Run in docker

You can run PyWatchPower in a containerized environment using the provided Docker image. The image is available on
Docker Hub as `corvis/py-watch-power`.

```bash
docker run -d --name py-watch-power --priviliged corvis/py-watch-power
```

# Credits

* Dmitry Berezovsky, author
* David Nedved, developer of
  the [docker-voltronic-homeassistant](https://github.com/ned-kelly/docker-voltronic-homeassistant), which was used as a
  reference and a source of inspiration.
* 'Skymax', who did original research on the protocol
  and [published it on his blog](https://skyboo.net/2017/03/monitoring-voltronic-power-axpert-mex-inverter-under-linux/).

# Disclaimer

This module is licensed under GPL-3.0. It doesn't allow you to use it in a commercial product without making your
product open source and comes with no warranty. Please see the included LICENSE file for details.
