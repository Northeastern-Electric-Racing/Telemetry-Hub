import os
import json
from datetime import datetime
import random

from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy, QFrame, QTabWidget
)
from PyQt6.QtCore import QUrl, QTimer, Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

from ner_telhub.model.data_models import DataModelManager
from ner_telhub.widgets.styled_widgets import NERButton

MAP_SELECT_1 = "map_google.html"
MAP_SELECT_2 = 'map_car_perspective.html'
USE_TEST_DATA = 0  # Automatically generates model data in generate_test_data function
UPDATE_TIME_MS = 250


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)


class MapView(QWidget):
    """
    View for showing location data.
    """

    def __init__(self, parent: QWidget, model: DataModelManager):
        super(MapView, self).__init__(parent)

        # Dashboard title
        title_label = QLabel("NER GPS Live View")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        # Telemetry data labels
        self.speed_label = QLabel("Speed: 0 Mph")
        self.heading_label = QLabel("Heading: 0 °")
        self.voltage_label = QLabel("12V System Voltage: 0 V")
        self.pack_soc_label = QLabel("Pack SOC: 0 %")

        # Top telemetry data layout
        top_telemetry_layout = QHBoxLayout()
        top_telemetry_layout.addWidget(self.speed_label, stretch=1)
        top_telemetry_layout.addWidget(self.voltage_label, stretch=1)

        # Bottom telemetry data layout
        bottom_telemetry_layout = QHBoxLayout()
        bottom_telemetry_layout.addWidget(self.heading_label, stretch=1)
        bottom_telemetry_layout.addWidget(self.pack_soc_label, stretch=1)

        # Telemetry data frame
        telemetry_frame = QFrame()
        telemetry_frame.setFrameShape(QFrame.Shape.StyledPanel)
        telemetry_frame.setFrameShadow(QFrame.Shadow.Sunken)

        # Combine top and bottom telemetry layouts in a QVBoxLayout
        telemetry_layout = QVBoxLayout()
        telemetry_layout.addLayout(top_telemetry_layout)
        telemetry_layout.addLayout(bottom_telemetry_layout)

        telemetry_frame.setLayout(telemetry_layout)

        # Status label
        self.logging_status_label = QLabel("Logging: Yes")
        self.gps_status_label = QLabel("GPS Status: Connected")

        # Create a QHBoxLayout to hold the two status labels
        self.status_layout = QHBoxLayout()
        self.status_layout.addWidget(self.logging_status_label)
        self.status_layout.addWidget(self.gps_status_label)

        # Telemetry data frame
        self.telemetry_frame = QFrame()
        self.telemetry_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.telemetry_frame.setFrameShadow(QFrame.Shadow.Sunken)

        # Initialize map view
        self.map_view = QWebEngineView()
        self.map_view.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding)

        # Initialize the perspective Google Maps view
        self.perspective_view = QWebEngineView()
        self.perspective_view.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding)

        # Create a QTabWidget instance
        self.map_tabs = QTabWidget()

        # Add the map views to the tab widget
        self.map_tabs.addTab(self.map_view, "Line")
        self.map_tabs.addTab(self.perspective_view, "POV")

        self.button_clear = NERButton("Clear", NERButton.Styles.BLUE)
        self.button_clear.pressed.connect(self.callback_clear)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        layout.addWidget(title_label, stretch=0)
        layout.addWidget(telemetry_frame, stretch=0)
        # Use the map_tabs widget instead of map_stack
        layout.addWidget(self.map_tabs, stretch=1)
        layout.addWidget(self.button_clear, stretch=0)
        layout.addLayout(self.status_layout, stretch=0)

        # Initialize default data models
        self.model = model
        self.lat_data = [(datetime.now(), 42.339855)]
        self.lon_data = [(datetime.now(), -71.088706)]
        self.needupdate = 2  # used to compare to new length of data model to see if new data was generated as a condition to update the map
        self.gpsfix_data = 0
        self.gpsspeed_data = 0
        self.heading_data = 0
        self.twelvev_data = 0
        self.packsoc_data = 0
        self.logging_data = 0

        # Load in maps
        self.load_map1()
        self.load_map2()
        self.setLayout(layout)

        # Start timer
        self.timer = QTimer(self)
        self.timer.start(UPDATE_TIME_MS)

        # Update all data every UPDATE_TIME_MS
        self.timer.timeout.connect(self.update_map1)
        self.timer.timeout.connect(self.update_map2)
        if USE_TEST_DATA:
            self.timer.timeout.connect(self.generate_test_data)
        else:
            self.timer.timeout.connect(self.update_models)

    def load_map1(self):
        """
        Load the first map.
        """
        map_path = os.path.join(os.path.dirname(__file__), MAP_SELECT_1)
        with open(map_path, 'r', encoding='utf-8') as map_file:
            html = map_file.read()
            self.map_view.setHtml(html, QUrl("qrc:/"))
            page = self.map_view.page()
            channel = QWebChannel(page)
            page.setWebChannel(channel)

            # init map
            self.map_view.loadFinished.connect(
                lambda: page.runJavaScript("initMap();"))

    def load_map2(self):
        """
        Load the second map.
        """
        map_path = os.path.join(os.path.dirname(__file__), MAP_SELECT_2)
        with open(map_path, 'r', encoding='utf-8') as map_file:
            html = map_file.read()
            self.perspective_view.setHtml(html, QUrl("qrc:/"))
            page = self.perspective_view.page()
            channel = QWebChannel(page)
            page.setWebChannel(channel)

            lat_data_json = json.dumps(self.lat_data, cls=DateTimeEncoder)
            lon_data_json = json.dumps(self.lon_data, cls=DateTimeEncoder)
            heading_data_json = json.dumps(self.heading_data)

            # init map
            self.perspective_view.loadFinished.connect(
                lambda: page.runJavaScript(
                    "initMap();",
                    lambda _: page.runJavaScript(f"loadPath({lat_data_json}, {lon_data_json}, {heading_data_json});")))

    def update_map1(self):
        # Check if we need to update
        if not self.gpsfix_data or self.needupdate == len(self.lat_data):
            return
        # Convert lat_data and lon_data to JSON
        lat_data_json = json.dumps(self.lat_data, cls=DateTimeEncoder)
        lon_data_json = json.dumps(self.lon_data, cls=DateTimeEncoder)
        self.map_view.page().runJavaScript(
            f"loadPath({lat_data_json}, {lon_data_json});")

    def update_map2(self):
        # Check if we need to update
        if not self.gpsfix_data or self.needupdate == len(self.lat_data):
            return
        # Convert lat_data and lon_data and heading data to JSON
        lat_data_json = json.dumps(self.lat_data, cls=DateTimeEncoder)
        lon_data_json = json.dumps(self.lon_data, cls=DateTimeEncoder)
        heading_data_json = json.dumps(self.heading_data)
        self.perspective_view.page().runJavaScript(
            f"loadPath({lat_data_json}, {lon_data_json}, {heading_data_json});")

    def update_models(self):
        """
        Called periodically every UPDATE_TIME_MS to update all models to keep UI up to date
        """
        self.needupdate = len(
            self.lat_data)  # used to compare to new length of data model to see if new data was generated as a condition to update the map

        # Update latitude data model for map
        try:
            self.lat_data = self.model.getDataModel(108).getData()
        except Exception:
            self.lat_data = [
                (datetime.now(), 42.339855),
            ]

        # Update longitude data model for map
        try:
            self.lon_data = self.model.getDataModel(109).getData()
        except Exception:
            self.lon_data = [
                (datetime.now(), -71.088706),
            ]

        # Update heading data model for map
        try:
            self.heading_data = self.model.getDataModel(113).getLastestValue()
        except Exception:
            self.heading_data = 0
        self.heading_label.setText(f"Heading: {self.heading_data} °")

        try:
            self.logging_data = self.model.getDataModel(129).getLastestValue()
        except Exception:
            self.logging_data = 0
        self.logging_status_label.setText(
            f"Logging: {'Yes' if self.logging_data else 'No'}")

        try:
            self.gpsfix_data = self.model.getDataModel(110).getLastestValue()
        except Exception:
            self.gpsfix_data = 0
        self.gps_status_label.setText(
            f"GPS Status: {'Connected' if self.gpsfix_data else 'Disconnected'}")

        try:
            self.gpsspeed_data = self.model.getDataModel(112).getLastestValue()
        except Exception:
            self.gpsspeed_data = 0
        mphspeed = self.gpsspeed_data * 2.237
        self.speed_label.setText(f"Speed: {mphspeed} Mph")

        try:
            self.twelvev_data = self.model.getDataModel(63).getLastestValue()
        except Exception:
            self.twelvev_data = 0
        self.voltage_label.setText(f"12V System: {self.twelvev_data} V")

        try:
            self.packsoc_data = self.model.getDataModel(4).getLastestValue()
        except Exception:
            self.packsoc_data = 0
        self.pack_soc_label.setText(f"Pack SOC: {self.packsoc_data} %")

    # def callback_pause(self):
    #     """
    #     Called when the clear button is clicked AND stops updating the models by stopping UPDATETIME
    #     """
    #     self.timer.stop()

    def callback_clear(self):
        """
        Called when the clear button is clicked AND stops updating the models by stopping UPDATETIME
        """
        self.map_view.page().runJavaScript("clearPath();")
        self.perspective_view.page().runJavaScript("clearPath();")

    # def callback_plot(self):
    #     """
    #     Called when the plot button is clicked AND restarts updating the models by starting UPDATETIME
    #     """
    #     lat_data_json = json.dumps(self.lat_data, cls=DateTimeEncoder)
    #     lon_data_json = json.dumps(self.lon_data, cls=DateTimeEncoder)
    #     self.map_view.page().runJavaScript(f"loadPath({lat_data_json}, {lon_data_json});")
    #     self.timer.start(UPDATE_TIME_MS)

    def generate_test_data(self):
        """
        Called periodically every UPDATETIME to update all models over time for testing without live data
        """
        self.needupdate = len(
            self.lat_data)  # used to compare to new length of data model to see if new data was generated as a condition to update the map

        new_lat = self.lat_data[-1][1] + random.uniform(-0.000100, 0.000100)
        test_lat = (datetime.now(), new_lat)
        self.lat_data.append(test_lat)

        new_lon = self.lon_data[-1][1] + random.uniform(-0.000100, 0.000100)
        test_lon = (datetime.now(), new_lon)
        self.lon_data.append(test_lon)

        self.heading_data = self.heading_data + random.uniform(-10, 10)
        # Updates UI based on status
        self.heading_label.setText(f"Heading: {self.heading_data} °")

        self.gpsfix_data = random.choice([True, False])
        # Updates UI based on status
        self.gps_status_label.setText(
            f"GPS Status: {'Connected' if self.gpsfix_data else 'Disconnected'}")

        self.gpsspeed_data = self.gpsspeed_data + random.uniform(-20, 20)
        mphspeed = self.gpsspeed_data * 2.237
        # Updates UI based on status
        self.speed_label.setText(f"Speed: {mphspeed} Mph")

        self.twelvev_data = self.twelvev_data + random.uniform(-1, 1)
        # Updates UI based on status
        self.voltage_label.setText(f"12V System: {self.twelvev_data} V")

        self.packsoc_data = self.packsoc_data + random.uniform(-1, 1)
        # Updates UI based on status
        self.pack_soc_label.setText(f"Pack SOC: {self.packsoc_data} %")
