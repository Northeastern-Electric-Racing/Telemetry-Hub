# Telemetry Hub
This GUI Application allows for remote connection to the car using the Xbee wireless modules. The following functionality is planned on being supported:
- BMS configuration
- Remote operation and control
- General car configuration (EEPROM param settting, filters for data/wireless messages)
- Wireless parameter configuration (related to Zigbee network information)
- Sending and receiving CAN messages
- Graphical views of incoming data

## Tech Specs
The application is written in python using the PyQt GUI toolkit. The following resources are good for an introduction to PyQt:
- [General Qt description](https://wiki.qt.io/About_Qt)
- [Complete PyQt Tutorial](https://www.pythonguis.com/pyqt6-tutorial/)
- [Layouts](https://realpython.com/python-pyqt-layout/)
- [Threading](https://realpython.com/python-pyqt-qthread/)

Python resources:
- [Object-Oriented Guide](https://www.pythontutorial.net/python-oop/)
- [Documentation](https://realpython.com/documenting-python-code/)


## Setup and Installation
The pipenv library is used to extablish a virtual project environment. The only prerequisite is that you have python version 3.10 installed ([here](https://www.python.org/downloads/)).

Follow the steps below to run the project:
1. Clone the repo 
2. Install pipenv globally (`pip install --user pipenv`)
3. Navigate to the main directory (/Telemetry-Hub) and run `pipenv install` to install all project dependencies
4. Run `pipenv shell` to activate the virtual environment
5. Run `python app.py` in the /src/telhub package 

## Running the App
There are two ways to run the app:
1. Navigate to the `src` directory and run the command `python -m ner_telhub`
2. Run the python script `run.py` located in the `src` directory. This file exists as an entry point for pyinstaller to package an executable, but still can be used to run the app.
