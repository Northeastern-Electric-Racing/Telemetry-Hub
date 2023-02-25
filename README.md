# Telemetry Hub
This GUI Application allows for processing and display of data generated from the car. It is broken down into a series of Windows, each with different types of connections. These include:
- Vehicle Window: Processes data in real time from the car (usually using data from XBee wireless modules)
- SD Window: Processes log files saved to an SD card on the car
- Database Window: Allows interaction with data from hostorical vehicle sessions

It is written Python using the PyQt GUI framework for the frontend.

## Setup and Installation
The [pipenv](https://pypi.org/project/pipenv/) library is used to extablish a virtual project environment. The only prerequisite is that you have python version 3.10 installed ([here](https://www.python.org/downloads/)).

Follow the steps below to run the project:
1. Clone the repo (Navigate to your desired directory and run `git clone https://github.com/Northeastern-Electric-Racing/Telemetry-Hub.git`)
2. Install pipenv globally (`pip install --user pipenv`)
3. Navigate into the main directory (/Telemetry-Hub) and run `pipenv install` to install all project dependencies
4. Run `pipenv shell` to activate the virtual environment
5. Start the app with the command `python start.py`

After the inital run, only steps 4/5 will be needed to run the app again (enter the environment and start the app).

NOTE: If any of the commands in steps 2-5 fail, prepend them with `python -m` and try again.

## Tech Resources
The application is written in python using the PyQt GUI toolkit. The following resources are good for an introduction to PyQt:
- [General Qt description](https://wiki.qt.io/About_Qt)
- [Complete PyQt Tutorial](https://www.pythonguis.com/pyqt6-tutorial/)
- [Layouts](https://realpython.com/python-pyqt-layout/)
- [Threading](https://realpython.com/python-pyqt-qthread/)

Python resources:
- [Object-Oriented Guide](https://www.pythontutorial.net/python-oop/)
- [Documentation](https://realpython.com/documenting-python-code/)

## Formatting
We're using [autopep8](https://pypi.org/project/autopep8/) to automatically fix style errors with the code. Run using:

    autopep8 -iraa ner_telhub

To run on any other directory, just swap the name with `ner_telhub`.

It is also recommended to install a Python linting tool (if using VSCode you can easily install an extension). 

## Running Processing Library
To avoid the overhead of the GUI on large files, the ner_processing library can be run seperately. Follow the below steps:
1. Create a directory called `logs` in the project root (same level as `ner_processing`), and place the log files to process
2. Start using the command `python -m ner_processing`. The output file will be written to `output.csv` in the project root

## Deployment
In order to generate an executable, follow the below steps:
- Windows:
    - To build with the provided spec file, run: `pyinstaller telhub.spec`
    - To generate a spec file from scratch, run: `pyinstaller start.py --windowed --name=telhub --icon=resources/ner_logo.ico --add-data="resources;resources"`
    - The generated executable can then be found in `dist/telhub`

- Mac:
    - Not supported yet
