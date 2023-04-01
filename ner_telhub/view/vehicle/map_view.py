import os
import json
from PyQt6.QtCore import QDateTime, QUrl, QTimer, Qt
import sys
from ner_telhub.model.data_models import DataModelManager
from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, QWidget, QMessageBox, QApplication, QHBoxLayout, QSizePolicy, QFrame, QTabWidget, QStackedWidget, QTabBar, 
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from ner_telhub.widgets.styled_widgets import NERButton
from datetime import datetime, timedelta

map_select_1="map_google.html"
map_select_2='map_car_perspective.html'

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
        
        self.button_clear = NERButton("Clear", NERButton.Styles.BLUE)
        self.button_clear.pressed.connect(self.callback_clear)
        self.button_plot = NERButton("Plot", NERButton.Styles.BLUE)
        self.button_plot.pressed.connect(self.callback_plot)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.button_clear, stretch=0)
        button_layout.addWidget(self.button_plot, stretch=0)

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
        # Initialize status labels
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
        self.map_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Initialize the new Google Maps view
        self.new_map_view = QWebEngineView()
        self.new_map_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


        # Create a QTabWidget instance
        self.map_tabs = QTabWidget()

        # Add the map views to the tab widget
        self.map_tabs.addTab(self.map_view, "Line")
        self.map_tabs.addTab(self.new_map_view, "POV")

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        layout.addWidget(title_label, stretch=0)
        layout.addLayout(button_layout, stretch=0)
        layout.addWidget(telemetry_frame, stretch=0)
        layout.addWidget(self.map_tabs, stretch=1)  # Use the map_tabs widget instead of map_stack
        layout.addLayout(self.status_layout, stretch=0)
        
        #Initialize data models
        try:
            latitude_model = model.getDataModel(108)
            self.lat_data = latitude_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting latitude data. {e}")
            self.lat_data = [
                (datetime.now(), 42.339030),
            ]
            # self.lat_data = [
            #     (datetime(2023, 4, 1, 9, 0, 0), 37.7749),
            #     (datetime(2023, 4, 1, 9, 0, 10), 37.7753),
            #     (datetime(2023, 4, 1, 9, 0, 20), 37.7757),
            #     (datetime(2023, 4, 1, 9, 0, 30), 37.7761),
            #     (datetime(2023, 4, 1, 9, 0, 40), 37.7765),
            # ]
            
            
        try:
            longitude_model = model.getDataModel(109)
            self.lon_data = longitude_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting longitude data. {e}")
            self.lon_data = [
                (datetime.now(), -71.087913),
            ]
            # self.lon_data = [
            #     (datetime(2023, 4, 1, 9, 0, 0), -122.4194),
            #     (datetime(2023, 4, 1, 9, 0, 10), -122.4189),
            #     (datetime(2023, 4, 1, 9, 0, 20), -122.4184),
            #     (datetime(2023, 4, 1, 9, 0, 30), -122.4179),
            #     (datetime(2023, 4, 1, 9, 0, 40), -122.4174),
            # ]
        
        # try:
        #     logging_model = model.getDataModel(...)
        #     self.logging_data = logging_model.getData()
        # except Exception as e:
        #     #QMessageBox.critical(self, "Error", f"Error getting data. {e}")
        #     self.logging_data = [
        #         (datetime.now(), 0),
        #     ]

        try:
            gpsfix_model = model.getDataModel(110)
            self.gpsfix_data = gpsfix_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting data. {e}")
            self.gpsfix_data = [
                (datetime.now(), 0),
            ]

        try:
            gpsspeed_model = model.getDataModel(112)
            self.gpsspeed_data = gpsspeed_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting data. {e}")
            self.gpsspeed_data = [
                (datetime.now(), 0),
            ]

        try:
            heading_model = model.getDataModel(113)
            self.heading_data = heading_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting data. {e}")
            self.heading_data = [
                (datetime.now(), 0),
            ]
            # self.heading_data = [
            #     (datetime(2023, 4, 1, 9, 0, 0), 45),
            #     (datetime(2023, 4, 1, 9, 0, 10), 50),
            #     (datetime(2023, 4, 1, 9, 0, 20), 55),
            #     (datetime(2023, 4, 1, 9, 0, 30), 60),
            #     (datetime(2023, 4, 1, 9, 0, 40), 65),
            # ]

        try:
            twelvev_model = model.getDataModel(113)
            self.twelvev_data = twelvev_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting data. {e}")
            self.twelvev_data = [
                (datetime.now(), 0),
            ]

        try:
            packsoc_model = model.getDataModel(113)
            self.packsoc_data = packsoc_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting data. {e}")
            self.packsoc_data = [
                (datetime.now(), 0),
            ]
            
        self.current_index = len(self.lat_data)
        self.load_map1()
        self.load_map2()
        self.setLayout(layout)
        self.timer = QTimer(self)
        #self.timer.timeout.connect(self.update_logging_status)
        self.timer.timeout.connect(self.update_gpsspeed)
        self.timer.timeout.connect(self.update_heading)
        self.timer.timeout.connect(self.update_batteryvoltage)
        self.timer.timeout.connect(self.update_packsoc)
        self.timer.timeout.connect(self.update_gps_status)
        self.timer.timeout.connect(self.update_map1)
        self.timer.timeout.connect(self.update_map2)
        updatetime=250 #ms
        self.timer.start(updatetime)  # Call the update_map function every 250ms.



    def load_map1(self):
        #map_path = os.path.join(os.path.dirname(__file__), "map.html") #For free maps
        
        self.page = self.map_view.page()
        channel = QWebChannel(self.page) 
        self.page.setWebChannel(channel)

        map_path = os.path.join(os.path.dirname(__file__), map_select_1)
        with open(map_path, 'r', encoding='utf-8') as map_file:
            html = map_file.read()
            self.map_view.setHtml(html)

            self.map_view.setHtml(html, QUrl("qrc:/"))
            page = self.map_view.page()
            channel = QWebChannel(page)
            page.setWebChannel(channel)

            # Convert lat_data and lon_data to JSON
            lat_data_json = json.dumps(self.lat_data, cls=DateTimeEncoder)
            lon_data_json = json.dumps(self.lon_data, cls=DateTimeEncoder)

            # Inject data into the HTML file by calling the loadPath function depening on which map config selected
            if (map_select_1=="map_openstreetmap.html"):
                self.map_view.loadFinished.connect(lambda: page.runJavaScript(f"loadPath({lat_data_json}, {lon_data_json});"))
            else:
                self.map_view.loadFinished.connect(lambda: page.runJavaScript("initMap();", lambda _: page.runJavaScript(f"loadPath({lat_data_json}, {lon_data_json});")))

    def load_map2(self):
        self.page = self.new_map_view.page()
        channel = QWebChannel(self.page) 
        self.page.setWebChannel(channel)

        map_path = os.path.join(os.path.dirname(__file__), map_select_2)
        with open(map_path, 'r', encoding='utf-8') as map_file:
            html = map_file.read()
            self.new_map_view.setHtml(html)

            self.new_map_view.setHtml(html, QUrl("qrc:/"))
            page = self.new_map_view.page()
            channel = QWebChannel(page)
            page.setWebChannel(channel)

            # Convert lat_data and lon_data to JSON
            lat_data_json = json.dumps(self.lat_data, cls=DateTimeEncoder)
            lon_data_json = json.dumps(self.lon_data, cls=DateTimeEncoder)
            heading_data_json = json.dumps(self.heading_data[-1][1])
            # Inject data into the HTML file by calling the loadPath function depening on which map config selected
            self.new_map_view.loadFinished.connect(lambda: page.runJavaScript("initMap();", lambda _: page.runJavaScript(f"loadPath({lat_data_json}, {lon_data_json}, {heading_data_json});")))
            
    def update_map1(self):
        
        try:
            latitude_model = model.getDataModel(108)
            self.lat_data = latitude_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting latitude data. {e}")
            self.lat_data = [
                (datetime.now(), 42.339030),
            ]
            # self.lat_data = [
            #     (datetime(2023, 4, 1, 9, 0, 0), 37.7749),
            #     (datetime(2023, 4, 1, 9, 0, 10), 37.7753),
            #     (datetime(2023, 4, 1, 9, 0, 20), 37.7757),
            #     (datetime(2023, 4, 1, 9, 0, 30), 37.7761),
            #     (datetime(2023, 4, 1, 9, 0, 40), 37.7765),
            # ]

        try:
            longitude_model = model.getDataModel(109)
            self.lon_data = longitude_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting longitude data. {e}")
            self.lon_data = [
                (datetime.now(), -71.087913),
            ]
            # self.lon_data = [
            #     (datetime(2023, 4, 1, 9, 0, 0), -122.4194),
            #     (datetime(2023, 4, 1, 9, 0, 10), -122.4189),
            #     (datetime(2023, 4, 1, 9, 0, 20), -122.4184),
            #     (datetime(2023, 4, 1, 9, 0, 30), -122.4179),
            #     (datetime(2023, 4, 1, 9, 0, 40), -122.4174),
            # ]
            

        if self.current_index >= len(self.lat_data):
            return
        
        try:
            # Convert lat_data and lon_data to JSON
            lat_data_json = json.dumps(self.lat_data, cls=DateTimeEncoder)
            lon_data_json = json.dumps(self.lon_data, cls=DateTimeEncoder)
            self.map_view.page().runJavaScript(f"loadPath({lat_data_json}, {lon_data_json});")
            self.current_index=len(self.lat_data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error plotting next datapoint: {e}")
    
    def update_map2(self):
        
        try:
            latitude_model = model.getDataModel(108)
            self.lat_data = latitude_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting latitude data. {e}")
            self.lat_data = [
                (datetime.now(), 42.339030),
            ]
            # self.lat_data = [
            #     (datetime(2023, 4, 1, 9, 0, 0), 37.7749),
            #     (datetime(2023, 4, 1, 9, 0, 10), 37.7753),
            #     (datetime(2023, 4, 1, 9, 0, 20), 37.7757),
            #     (datetime(2023, 4, 1, 9, 0, 30), 37.7761),
            #     (datetime(2023, 4, 1, 9, 0, 40), 37.7765),
            # ]

        try:
            longitude_model = model.getDataModel(109)
            self.lon_data = longitude_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting longitude data. {e}")
            self.lon_data = [
                (datetime.now(), -71.087913),
            ]
            # self.lon_data = [
            #     (datetime(2023, 4, 1, 9, 0, 0), -122.4194),
            #     (datetime(2023, 4, 1, 9, 0, 10), -122.4189),
            #     (datetime(2023, 4, 1, 9, 0, 20), -122.4184),
            #     (datetime(2023, 4, 1, 9, 0, 30), -122.4179),
            #     (datetime(2023, 4, 1, 9, 0, 40), -122.4174),
            # ]

        try:
            heading_model = model.getDataModel(113)
            self.heading_data = heading_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting data. {e}")
            self.heading_data = [
                (datetime.now(), 0),
            ]
            # self.heading_data = [
            #     (datetime(2023, 4, 1, 9, 0, 0), 45),
            #     (datetime(2023, 4, 1, 9, 0, 10), 50),
            #     (datetime(2023, 4, 1, 9, 0, 20), 55),
            #     (datetime(2023, 4, 1, 9, 0, 30), 60),
            #     (datetime(2023, 4, 1, 9, 0, 40), 65),
            # ]
        
        if self.current_index >= len(self.lat_data):
            return
        
        try:
            # Convert lat_data and lon_data to JSON
            lat_data_json = json.dumps(self.lat_data, cls=DateTimeEncoder)
            lon_data_json = json.dumps(self.lon_data, cls=DateTimeEncoder)
            heading_data_json = json.dumps(self.heading_data[-1][1])
            print(json.dumps(self.heading_data[-1][1]))
            self.new_map_view.page().runJavaScript(f"loadPath({lat_data_json}, {lon_data_json}, {heading_data_json});")
            self.current_index=len(self.lat_data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error plotting next datapoint: {e}")
        
    def callback_clear(self):
        """
        Called when the clear button is clicked.
        """
        self.map_view.page().runJavaScript("clearPath();")
        self.timer.stop()
        
    def callback_plot(self):
        """
        Called when the plot button is clicked.
        """
        lat_data_json = json.dumps(self.lat_data, cls=DateTimeEncoder)
        lon_data_json = json.dumps(self.lon_data, cls=DateTimeEncoder)
        self.map_view.page().runJavaScript(f"loadPath({lat_data_json}, {lon_data_json});")
        self.timer.start(updatetime)
        
    # def update_logging_status(self):
        # try:
        #     logging_model = model.getDataModel(...)
        #     self.logging_data = logging_model.getData()
        # except Exception as e:
        #     #QMessageBox.critical(self, "Error", f"Error getting data. {e}")
        #     self.logging_data = [
        #         (datetime.now(), 0),
        #     ]
    #     self.logging_status_label.setText(f"Logging: {'Yes' if self.gpsfix_data[-1][1] 'No'}")

    def update_gps_status(self):
        try:
            gpsfix_model = model.getDataModel(110)
            self.gpsfix_data = gpsfix_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting data. {e}")
            self.gpsfix_data = [
                (datetime.now(), 0),
            ]
        self.gps_status_label.setText(f"GPS Status: {'Connected' if self.gpsfix_data[-1][1] else 'Disconnected'}")

    def update_gpsspeed(self):
        try:
            gpsspeed_model = model.getDataModel(112)
            self.gpsspeed_data = gpsspeed_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting data. {e}")
            self.gpsspeed_data = [
                (datetime.now(), 0),
            ]
        mphspeed=self.gpsspeed_data[-1][1]*2.237
        self.speed_label.setText(f"Speed: {mphspeed} Mph")

    def update_heading(self):
        try:
            heading_model = model.getDataModel(113)
            self.heading_data = heading_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting data. {e}")
            self.heading_data = [
                (datetime.now(), 0),
            ]
        self.heading_label.setText(f"Heading: {self.heading_data[-1][1]} °")
    
    def update_batteryvoltage(self):
        try:
            twelvev_model = model.getDataModel(113)
            self.twelvev_data = twelvev_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting data. {e}")
            self.twelvev_data = [
                (datetime.now(), 0),
            ]
        self.voltage_label.setText(f"12V System: {self.twelvev_data[-1][1]} V")


    def update_packsoc(self):
        try:
            packsoc_model = model.getDataModel(113)
            self.packsoc_data = packsoc_model.getData()
        except Exception as e:
            #QMessageBox.critical(self, "Error", f"Error getting data. {e}")
            self.packsoc_data = [
                (datetime.now(), 0),
            ]
        self.pack_soc_label.setText(f"Pack SOC: {self.packsoc_data[-1][1]} %")
    
